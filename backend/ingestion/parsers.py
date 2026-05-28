import pandas as pd
from decimal import Decimal
from datetime import datetime, date
import re


UNIT_CONVERSION = {
    'mwh': ('kwh', Decimal('1000')),
    'gwh': ('kwh', Decimal('1000000')),
    'kwh': ('kwh', Decimal('1')),
    'liter': ('liter', Decimal('1')),
    'litre': ('liter', Decimal('1')),
    'l': ('liter', Decimal('1')),
    'gallon': ('liter', Decimal('3.78541')),
    'gal': ('liter', Decimal('3.78541')),
    'kg': ('kg', Decimal('1')),
    'kilogram': ('kg', Decimal('1')),
    'tonne': ('kg', Decimal('1000')),
    'ton': ('kg', Decimal('1000')),
    'mt': ('kg', Decimal('1000')),
    'km': ('km', Decimal('1')),
    'kilometer': ('km', Decimal('1')),
    'mile': ('km', Decimal('1.60934')),
    'miles': ('km', Decimal('1.60934')),
    'm3': ('m3', Decimal('1')),
}

EMISSION_FACTORS = {
    'diesel_liter': Decimal('2.68'),
    'petrol_liter': Decimal('2.31'),
    'natural_gas_m3': Decimal('2.04'),
    'electricity_kwh': Decimal('0.233'),
    'flight_km': Decimal('0.255'),
    'hotel_night': Decimal('31.0'),
    'ground_km': Decimal('0.089'),
}


def normalize_unit(quantity, unit_str):
    unit_clean = unit_str.strip().lower()
    if unit_clean in UNIT_CONVERSION:
        target_unit, factor = UNIT_CONVERSION[unit_clean]
        return Decimal(str(quantity)) * factor, target_unit
    return Decimal(str(quantity)), unit_clean


def parse_date_flexible(date_str):
    if not date_str or pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    formats = [
        '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y',
        '%Y%m%d', '%d-%m-%Y', '%Y/%m/%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def flag_suspicious(quantity, category):
    reasons = []
    if quantity <= 0:
        reasons.append('quantity is zero or negative')
    thresholds = {
        'fuel': Decimal('100000'),
        'electricity': Decimal('1000000'),
        'flight': Decimal('50000'),
        'hotel': Decimal('365'),
        'ground': Decimal('10000'),
        'procurement': Decimal('500000'),
    }
    for key, threshold in thresholds.items():
        if key in category.lower() and quantity > threshold:
            reasons.append(f'quantity exceeds expected threshold for {key}')
    return reasons


def _apply_extra_suspicion_checks(suspicion_reasons, quantity):
    """
    Additional checks on top of flag_suspicious():
    - Negative quantity (flag_suspicious catches <= 0, this is explicit for clarity)
    - Quantity exceeds hard limit of 100000
    """
    if quantity < 0:
        if 'quantity is zero or negative' not in suspicion_reasons:
            suspicion_reasons.append('quantity is negative')
    if quantity > Decimal('100000'):
        if not any('exceeds' in r for r in suspicion_reasons):
            suspicion_reasons.append('quantity exceeds 100000 threshold')
    return suspicion_reasons


class SAPParser:
    """
    Handles SAP flat file exports. In most enterprise setups, SAP data is
    extracted via transaction SE16 or MB51 into a pipe-delimited or
    tab-delimited flat file. Column headers may appear in German depending
    on system locale. We handle a normalized subset of fuel and procurement
    records from material movement data (transaction type 101, 261).
    """

    COLUMN_MAP = {
        'MBLNR': 'document_number',
        'MATNR': 'material_number',
        'MAKTX': 'material_description',
        'WERKS': 'plant_code',
        'MENGE': 'quantity',
        'MEINS': 'unit',
        'BUDAT': 'posting_date',
        'BWART': 'movement_type',
        'KOSTL': 'cost_center',
        'DMBTR': 'amount',
        'WAERS': 'currency',
        'document_number': 'document_number',
        'material_number': 'material_number',
        'material_description': 'material_description',
        'plant_code': 'plant_code',
        'quantity': 'quantity',
        'unit': 'unit',
        'posting_date': 'posting_date',
        'movement_type': 'movement_type',
        'cost_center': 'cost_center',
        'amount': 'amount',
        'currency': 'currency',
    }

    FUEL_MATERIALS = ['diesel', 'petrol', 'gasoline', 'natural gas', 'lng', 'cng', 'fuel oil']
    PROCUREMENT_MATERIALS = ['electricity', 'power', 'energy']

    def parse(self, file_path):
        results = []
        errors = []

        try:
            try:
                df = pd.read_csv(file_path, sep='|', encoding='utf-8', dtype=str)
            except Exception:
                df = pd.read_csv(file_path, sep='\t', encoding='utf-8', dtype=str)

            df.columns = [self.COLUMN_MAP.get(col.strip(), col.strip().lower()) for col in df.columns]
            df = df.fillna('')

            for idx, row in df.iterrows():
                try:
                    result = self._parse_row(row, idx)
                    if result:
                        results.append(result)
                except Exception as e:
                    errors.append({
                        'row_number': idx + 2,
                        'raw_data': row.to_dict(),
                        'error_message': str(e),
                    })

        except Exception as e:
            errors.append({
                'row_number': 0,
                'raw_data': {},
                'error_message': f'File could not be parsed: {str(e)}',
            })

        return results, errors

    def _parse_row(self, row, idx):
        quantity_str = str(row.get('quantity', '0')).replace(',', '.').strip()
        if not quantity_str:
            raise ValueError('Missing quantity')

        quantity = Decimal(quantity_str)
        unit = str(row.get('unit', 'liter')).strip()
        description = str(row.get('material_description', '')).lower()
        posting_date = parse_date_flexible(row.get('posting_date'))

        if not posting_date:
            raise ValueError(f"Invalid date: {row.get('posting_date')}")

        normalized_qty, normalized_unit = normalize_unit(quantity, unit)

        category, scope, emission_factor, co2e = self._classify_material(description, normalized_qty, normalized_unit)

        suspicion_reasons = flag_suspicious(normalized_qty, category)
        suspicion_reasons = _apply_extra_suspicion_checks(suspicion_reasons, normalized_qty)

        status = 'suspicious' if suspicion_reasons else 'pending'

        return {
            'scope': scope,
            'category': category,
            'subcategory': description[:100],
            'activity_description': f"SAP material movement: {row.get('material_description', '')} at plant {row.get('plant_code', '')}",
            'raw_quantity': quantity,
            'raw_unit': unit,
            'normalized_quantity': normalized_qty,
            'normalized_unit': normalized_unit,
            'emission_factor': emission_factor,
            'co2e_kg': co2e,
            'source_row_id': str(row.get('document_number', f'row_{idx}')),
            'raw_data': row.to_dict(),
            'period_start': posting_date,
            'period_end': posting_date,
            'suspicion_reason': '; '.join(suspicion_reasons),
            'status': status,
        }

    def _classify_material(self, description, quantity, unit):
        for fuel in self.FUEL_MATERIALS:
            if fuel in description:
                if 'natural gas' in description or 'lng' in description or 'cng' in description:
                    ef = EMISSION_FACTORS['natural_gas_m3']
                    co2e = quantity * ef if unit == 'm3' else None
                    return 'fuel_natural_gas', 1, ef, co2e
                else:
                    ef = EMISSION_FACTORS['diesel_liter'] if 'diesel' in description else EMISSION_FACTORS['petrol_liter']
                    co2e = quantity * ef if unit == 'liter' else None
                    return 'fuel_liquid', 1, ef, co2e

        for proc in self.PROCUREMENT_MATERIALS:
            if proc in description:
                ef = EMISSION_FACTORS['electricity_kwh']
                co2e = quantity * ef if unit == 'kwh' else None
                return 'electricity_procurement', 2, ef, co2e

        return 'procurement_other', 3, None, None


class UtilityParser:
    """
    Handles utility portal CSV exports. Most Indian and international utility
    portals (BESCOM, Tata Power, MSEDCL) allow monthly CSV download from their
    commercial customer portals. The export typically includes meter number,
    billing period start/end, units consumed in kWh, and tariff slab.
    Billing periods do not align with calendar months so we store them as-is.
    """

    COLUMN_MAP = {
        'meter_number': 'meter_number',
        'meter_id': 'meter_number',
        'account_number': 'meter_number',
        'billing_period_start': 'period_start',
        'period_start': 'period_start',
        'from_date': 'period_start',
        'billing_period_end': 'period_end',
        'period_end': 'period_end',
        'to_date': 'period_end',
        'units_consumed': 'units_consumed',
        'consumption_kwh': 'units_consumed',
        'kwh': 'units_consumed',
        'units': 'units_consumed',
        'unit': 'raw_unit',
        'consumption_unit': 'raw_unit',
        'facility': 'facility_name',
        'facility_name': 'facility_name',
        'location': 'facility_name',
        'tariff': 'tariff_category',
        'tariff_category': 'tariff_category',
        'tariff_slab': 'tariff_category',
    }

    def parse(self, file_path):
        results = []
        errors = []

        try:
            df = pd.read_csv(file_path, dtype=str)
            df.columns = [self.COLUMN_MAP.get(col.strip().lower(), col.strip().lower()) for col in df.columns]
            df = df.fillna('')

            for idx, row in df.iterrows():
                try:
                    result = self._parse_row(row, idx)
                    if result:
                        results.append(result)
                except Exception as e:
                    errors.append({
                        'row_number': idx + 2,
                        'raw_data': row.to_dict(),
                        'error_message': str(e),
                    })

        except Exception as e:
            errors.append({
                'row_number': 0,
                'raw_data': {},
                'error_message': f'File could not be parsed: {str(e)}',
            })

        return results, errors

    def _parse_row(self, row, idx):
        units_str = str(row.get('units_consumed', '0')).replace(',', '').strip()
        if not units_str:
            raise ValueError('Missing consumption value')

        quantity = Decimal(units_str)
        raw_unit = str(row.get('raw_unit', 'kwh')).strip().lower() or 'kwh'
        normalized_qty, normalized_unit = normalize_unit(quantity, raw_unit)

        period_start = parse_date_flexible(row.get('period_start'))
        period_end = parse_date_flexible(row.get('period_end'))

        if not period_start:
            raise ValueError(f"Invalid period start: {row.get('period_start')}")
        if not period_end:
            period_end = period_start

        ef = EMISSION_FACTORS['electricity_kwh']
        co2e = normalized_qty * ef if normalized_unit == 'kwh' else None

        suspicion_reasons = flag_suspicious(normalized_qty, 'electricity')
        suspicion_reasons = _apply_extra_suspicion_checks(suspicion_reasons, normalized_qty)

        status = 'suspicious' if suspicion_reasons else 'pending'

        facility = str(row.get('facility_name', 'unknown facility'))

        return {
            'scope': 2,
            'category': 'electricity',
            'subcategory': str(row.get('tariff_category', '')),
            'activity_description': f"Electricity consumption at {facility}, meter {row.get('meter_number', 'N/A')}",
            'raw_quantity': quantity,
            'raw_unit': raw_unit,
            'normalized_quantity': normalized_qty,
            'normalized_unit': normalized_unit,
            'emission_factor': ef,
            'co2e_kg': co2e,
            'source_row_id': str(row.get('meter_number', f'row_{idx}')),
            'raw_data': row.to_dict(),
            'period_start': period_start,
            'period_end': period_end,
            'suspicion_reason': '; '.join(suspicion_reasons),
            'status': status,
        }


class TravelParser:
    """
    Handles corporate travel exports from platforms like Concur or Navan.
    Both platforms support CSV exports from their reporting module.
    Concur exports typically include trip segments with origin/destination
    airport codes, travel class, booking date, and expense category.
    Distance is not always present so we use a standard average distance
    lookup for common routes and a fallback of 1000km for unknown routes.
    """

    COLUMN_MAP = {
        'trip_id': 'trip_id',
        'booking_id': 'trip_id',
        'employee_id': 'employee_id',
        'traveler_id': 'employee_id',
        'travel_date': 'travel_date',
        'departure_date': 'travel_date',
        'date': 'travel_date',
        'travel_type': 'travel_type',
        'segment_type': 'travel_type',
        'type': 'travel_type',
        'origin': 'origin',
        'from': 'origin',
        'departure': 'origin',
        'destination': 'destination',
        'to': 'destination',
        'arrival': 'destination',
        'distance_km': 'distance_km',
        'distance': 'distance_km',
        'km': 'distance_km',
        'travel_class': 'travel_class',
        'class': 'travel_class',
        'cabin_class': 'travel_class',
        'nights': 'nights',
        'hotel_nights': 'nights',
        'duration_nights': 'nights',
    }

    AIRPORT_DISTANCES = {
        ('DEL', 'BOM'): 1148, ('BOM', 'DEL'): 1148,
        ('DEL', 'BLR'): 1740, ('BLR', 'DEL'): 1740,
        ('DEL', 'MAA'): 1754, ('MAA', 'DEL'): 1754,
        ('BOM', 'BLR'): 842,  ('BLR', 'BOM'): 842,
        ('DEL', 'CCU'): 1305, ('CCU', 'DEL'): 1305,
        ('DEL', 'LHR'): 6713, ('LHR', 'DEL'): 6713,
        ('DEL', 'JFK'): 11766, ('JFK', 'DEL'): 11766,
        ('BOM', 'DXB'): 1924, ('DXB', 'BOM'): 1924,
    }

    CLASS_MULTIPLIERS = {
        'economy': Decimal('1.0'),
        'premium economy': Decimal('1.6'),
        'business': Decimal('2.9'),
        'first': Decimal('4.0'),
    }

    def parse(self, file_path):
        results = []
        errors = []

        try:
            df = pd.read_csv(file_path, dtype=str)
            df.columns = [self.COLUMN_MAP.get(col.strip().lower(), col.strip().lower()) for col in df.columns]
            df = df.fillna('')

            for idx, row in df.iterrows():
                try:
                    result = self._parse_row(row, idx)
                    if result:
                        results.append(result)
                except Exception as e:
                    errors.append({
                        'row_number': idx + 2,
                        'raw_data': row.to_dict(),
                        'error_message': str(e),
                    })

        except Exception as e:
            errors.append({
                'row_number': 0,
                'raw_data': {},
                'error_message': f'File could not be parsed: {str(e)}',
            })

        return results, errors

    def _parse_row(self, row, idx):
        travel_type = str(row.get('travel_type', 'flight')).strip().lower()
        travel_date = parse_date_flexible(row.get('travel_date'))

        if not travel_date:
            raise ValueError(f"Invalid travel date: {row.get('travel_date')}")

        if 'flight' in travel_type or 'air' in travel_type:
            return self._parse_flight(row, idx, travel_date)
        elif 'hotel' in travel_type or 'accommodation' in travel_type:
            return self._parse_hotel(row, idx, travel_date)
        else:
            return self._parse_ground(row, idx, travel_date)

    def _parse_flight(self, row, idx, travel_date):
        origin = str(row.get('origin', '')).strip().upper()
        destination = str(row.get('destination', '')).strip().upper()

        distance_str = str(row.get('distance_km', '')).strip()
        if distance_str and distance_str != 'nan':
            distance = Decimal(distance_str.replace(',', ''))
        else:
            distance = Decimal(str(self.AIRPORT_DISTANCES.get((origin, destination), 1000)))

        travel_class = str(row.get('travel_class', 'economy')).strip().lower()
        multiplier = self.CLASS_MULTIPLIERS.get(travel_class, Decimal('1.0'))

        ef = EMISSION_FACTORS['flight_km']
        co2e = distance * ef * multiplier

        suspicion_reasons = flag_suspicious(distance, 'flight')
        suspicion_reasons = _apply_extra_suspicion_checks(suspicion_reasons, distance)

        status = 'suspicious' if suspicion_reasons else 'pending'

        return {
            'scope': 3,
            'category': 'business_travel_flight',
            'subcategory': travel_class,
            'activity_description': f"Flight {origin} to {destination} ({travel_class})",
            'raw_quantity': distance,
            'raw_unit': 'km',
            'normalized_quantity': distance,
            'normalized_unit': 'km',
            'emission_factor': ef * multiplier,
            'co2e_kg': co2e,
            'source_row_id': str(row.get('trip_id', f'row_{idx}')),
            'raw_data': row.to_dict(),
            'period_start': travel_date,
            'period_end': travel_date,
            'suspicion_reason': '; '.join(suspicion_reasons),
            'status': status,
        }

    def _parse_hotel(self, row, idx, travel_date):
        nights_str = str(row.get('nights', '1')).strip()
        try:
            nights = Decimal(nights_str)
        except Exception:
            nights = Decimal('1')

        ef = EMISSION_FACTORS['hotel_night']
        co2e = nights * ef

        suspicion_reasons = flag_suspicious(nights, 'hotel')
        suspicion_reasons = _apply_extra_suspicion_checks(suspicion_reasons, nights)

        status = 'suspicious' if suspicion_reasons else 'pending'

        return {
            'scope': 3,
            'category': 'business_travel_hotel',
            'subcategory': str(row.get('destination', '')),
            'activity_description': f"Hotel stay at {row.get('destination', 'unknown')}, {nights} nights",
            'raw_quantity': nights,
            'raw_unit': 'nights',
            'normalized_quantity': nights,
            'normalized_unit': 'nights',
            'emission_factor': ef,
            'co2e_kg': co2e,
            'source_row_id': str(row.get('trip_id', f'row_{idx}')),
            'raw_data': row.to_dict(),
            'period_start': travel_date,
            'period_end': travel_date,
            'suspicion_reason': '; '.join(suspicion_reasons),
            'status': status,
        }

    def _parse_ground(self, row, idx, travel_date):
        distance_str = str(row.get('distance_km', '0')).strip()
        try:
            distance = Decimal(distance_str.replace(',', ''))
        except Exception:
            distance = Decimal('0')

        ef = EMISSION_FACTORS['ground_km']
        co2e = distance * ef

        suspicion_reasons = flag_suspicious(distance, 'ground')
        suspicion_reasons = _apply_extra_suspicion_checks(suspicion_reasons, distance)

        status = 'suspicious' if suspicion_reasons else 'pending'

        return {
            'scope': 3,
            'category': 'business_travel_ground',
            'subcategory': str(row.get('travel_type', 'ground')),
            'activity_description': f"Ground transport from {row.get('origin', 'unknown')} to {row.get('destination', 'unknown')}",
            'raw_quantity': distance,
            'raw_unit': 'km',
            'normalized_quantity': distance,
            'normalized_unit': 'km',
            'emission_factor': ef,
            'co2e_kg': co2e,
            'source_row_id': str(row.get('trip_id', f'row_{idx}')),
            'raw_data': row.to_dict(),
            'period_start': travel_date,
            'period_end': travel_date,
            'suspicion_reason': '; '.join(suspicion_reasons),
            'status': status,
        }