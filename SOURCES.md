# SOURCES

## SAP Export Research

The SAP parser design was inspired by common SAP flat-file exports generated from:

* SE16
* MB51
* material movement reports

Typical SAP fields such as:

* material number
* quantity
* movement type
* posting date
  were included.

---

## Utility Portal Research

Utility CSV structure was based on common exports from:

* Tata Power
* BESCOM
* MSEDCL

Typical fields:

* meter number
* billing period
* units consumed
* tariff category

---

## Corporate Travel Research

Travel exports were inspired by:

* SAP Concur
* Navan
* expense management systems

Common travel fields:

* origin
* destination
* travel class
* hotel nights
* distance

---

## Emission Factors

Sample emission factors were based on publicly available approximation values commonly used in ESG calculations.

The project uses simplified values for demonstration purposes.

---

## Real-World Considerations

Real enterprise ESG systems usually contain:

* inconsistent units
* missing values
* invalid dates
* duplicate records
* unexpected formats

The parsers were designed to handle these cases through:

* flexible parsing
* normalization
* validation
* suspicious record detection
