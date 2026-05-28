import { useEffect, useState } from 'react'
import axios from 'axios'

import {
  Database,
  Upload,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileSpreadsheet,
  BarChart3,
  Settings,
  Users,
  ShieldCheck,
} from 'lucide-react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'

const API_BASE_URL = 'https://breathe-esg-0rt4.onrender.com/api'

function App() {

  const [activeTab, setActiveTab] = useState('dashboard')

  const [clients, setClients] = useState([])
  const [records, setRecords] = useState([])

  const [selectedClient, setSelectedClient] = useState('')
  const [sourceType, setSourceType] = useState('sap')
  const [selectedFile, setSelectedFile] = useState(null)

  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchClients()
    fetchRecords()
  }, [])

  const fetchClients = async () => {

    try {

      const response = await axios.get(
        `${API_BASE_URL}/clients/`
      )

      setClients(response.data)

      if (response.data.length > 0) {
        setSelectedClient(response.data[0].id)
      }

    } catch (error) {
      console.log(error)
    }
  }

  const fetchRecords = async () => {

    try {

      const response = await axios.get(
        `${API_BASE_URL}/records/`
      )

      setRecords(response.data)

    } catch (error) {
      console.log(error)
    }
  }

  const handleUpload = async (e) => {

    e.preventDefault()

    if (!selectedFile) {
      setMessage('Please select a source file')
      return
    }

    const formData = new FormData()

    formData.append('client_id', selectedClient)
    formData.append('source_type', sourceType)
    formData.append('file', selectedFile)

    try {

      setLoading(true)

      const response = await axios.post(
        `${API_BASE_URL}/upload/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      setMessage(response.data.message)

      fetchRecords()

    } catch (error) {

      setMessage(
        error.response?.data?.error || 'Upload failed'
      )

    } finally {

      setLoading(false)

    }
  }

  const approveRecord = async (recordId) => {

    try {

      await axios.post(
        `${API_BASE_URL}/records/${recordId}/approve/`,
        {
          reviewed_by: 'ESG Analyst',
          review_notes: 'Approved after validation'
        }
      )

      fetchRecords()

    } catch (error) {
      console.log(error)
    }
  }

  const rejectRecord = async (recordId) => {

    try {

      await axios.post(
        `${API_BASE_URL}/records/${recordId}/reject/`,
        {
          reviewed_by: 'ESG Analyst',
          review_notes: 'Rejected during analyst review'
        }
      )

      fetchRecords()

    } catch (error) {
      console.log(error)
    }
  }

  const approvedCount = records.filter(
    record => record.status === 'approved'
  ).length

  const suspiciousCount = records.filter(
    record => record.status === 'suspicious'
  ).length

  const rejectedCount = records.filter(
    record => record.status === 'rejected'
  ).length

  return (

    <div className="min-h-screen flex bg-[#071028] text-white">

      {/* Sidebar */}

      <div className="w-[280px] bg-[#050b1f] border-r border-white/10 p-6 flex flex-col justify-between">

        <div>

          <div className="flex items-center gap-4 mb-14">

            <div className="bg-cyan-500/15 p-4 rounded-3xl">
              <Database className="text-cyan-400" size={34} />
            </div>

            <div>

              <h1 className="text-5xl font-black leading-none">
                Breathe
              </h1>

              <h1 className="text-5xl font-black leading-none">
                ESG
              </h1>

              <p className="text-slate-400 mt-2">
                Ingestion Engine
              </p>

            </div>

          </div>

          <div className="space-y-4">

            <SidebarItem
              icon={<BarChart3 size={22} />}
              title="Dashboard"
              active={activeTab === 'dashboard'}
              onClick={() => setActiveTab('dashboard')}
            />

            <SidebarItem
              icon={<Upload size={22} />}
              title="Upload Data"
              active={activeTab === 'upload'}
              onClick={() => setActiveTab('upload')}
            />

            <SidebarItem
              icon={<FileSpreadsheet size={22} />}
              title="Records"
              active={activeTab === 'records'}
              onClick={() => setActiveTab('records')}
            />

            <SidebarItem
              icon={<Users size={22} />}
              title="Clients"
              active={activeTab === 'clients'}
              onClick={() => setActiveTab('clients')}
            />

            <SidebarItem
              icon={<ShieldCheck size={22} />}
              title="Audit Logs"
              active={activeTab === 'audit'}
              onClick={() => setActiveTab('audit')}
            />

            <SidebarItem
              icon={<Settings size={22} />}
              title="Settings"
              active={activeTab === 'settings'}
              onClick={() => setActiveTab('settings')}
            />

          </div>

        </div>

        <div className="bg-gradient-to-br from-cyan-500/15 to-blue-600/15 border border-cyan-400/20 rounded-3xl p-6">

          <h2 className="text-2xl font-bold">
            ESG Analytics
          </h2>

          <p className="text-slate-300 text-sm mt-3 leading-7">
            Enterprise-grade ingestion and analyst review workflow.
          </p>

        </div>

      </div>

      {/* Main */}

      <div className="flex-1 p-8 overflow-auto">

        {/* DASHBOARD */}

        {
          activeTab === 'dashboard' && (

            <>

              <div className="bg-white/5 border border-white/10 rounded-[32px] p-10 backdrop-blur-xl shadow-2xl">

                <h1 className="text-6xl font-black tracking-tight">
                  ESG Ingestion Dashboard
                </h1>

                <p className="text-slate-400 mt-5 text-xl">
                  Multi-source emissions ingestion and analyst review system
                </p>

              </div>

              <div className="grid grid-cols-4 gap-6 mt-10">

                <StatsCard
                  title="Total Records"
                  value={records.length}
                  color="cyan"
                  icon={<Database />}
                />

                <StatsCard
                  title="Approved"
                  value={approvedCount}
                  color="green"
                  icon={<CheckCircle2 />}
                />

                <StatsCard
                  title="Suspicious"
                  value={suspiciousCount}
                  color="yellow"
                  icon={<AlertTriangle />}
                />

                <StatsCard
                  title="Rejected"
                  value={rejectedCount}
                  color="red"
                  icon={<XCircle />}
                />

              </div>

            </>

          )
        }

        {/* UPLOAD */}

        {
          activeTab === 'upload' && (

            <div className="bg-white/5 border border-white/10 rounded-[32px] p-10 backdrop-blur-xl">

              <div className="flex items-center gap-5 mb-8">

                <div className="bg-cyan-500/15 p-4 rounded-3xl">
                  <Upload className="text-cyan-400" size={28} />
                </div>

                <div>

                  <h2 className="text-4xl font-bold">
                    Upload Source Data
                  </h2>

                  <p className="text-slate-400 mt-2">
                    Upload CSV / Excel exports from enterprise systems
                  </p>

                </div>

              </div>

              <form
                onSubmit={handleUpload}
                className="grid grid-cols-4 gap-6"
              >

                <select
                  value={selectedClient}
                  onChange={(e) => setSelectedClient(e.target.value)}
                  className="bg-[#0b1328] border border-white/10 rounded-3xl px-6 py-5 text-lg outline-none focus:border-cyan-400"
                >
                  {
                    clients.map(client => (
                      <option
                        key={client.id}
                        value={client.id}
                      >
                        {client.name}
                      </option>
                    ))
                  }
                </select>

                <select
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                  className="bg-[#0b1328] border border-white/10 rounded-3xl px-6 py-5 text-lg outline-none focus:border-cyan-400"
                >
                  <option value="sap">SAP Export</option>
                  <option value="utility">Utility Data</option>
                  <option value="travel">Travel Data</option>
                </select>

                <input
                  type="file"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="bg-[#0b1328] border border-white/10 rounded-3xl px-6 py-5"
                />

                <button
                  type="submit"
                  disabled={loading}
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 rounded-3xl font-bold text-lg hover:scale-[1.02] transition-all duration-300 shadow-xl"
                >
                  {
                    loading
                      ? 'Uploading...'
                      : 'Upload File'
                  }
                </button>

              </form>

              {
                message && (
                  <div className="mt-6 bg-emerald-500/10 border border-emerald-400/20 rounded-3xl px-6 py-5 text-emerald-300 text-lg">
                    {message}
                  </div>
                )
              }

            </div>

          )
        }

        {/* RECORDS */}

        {
          activeTab === 'records' && (

            <div className="bg-white/5 border border-white/10 rounded-[32px] p-10 backdrop-blur-xl">

              <h2 className="text-4xl font-bold">
                Ingested Emission Records
              </h2>

              <p className="text-slate-400 mt-3">
                Analyst validation workflow
              </p>

              <div className="overflow-x-auto mt-8">

                <table className="w-full">

                  <thead>

                    <tr className="text-slate-400 border-b border-white/10">

                      <th className="text-left py-5 text-lg">
                        Category
                      </th>

                      <th className="text-left py-5 text-lg">
                        Scope
                      </th>

                      <th className="text-left py-5 text-lg">
                        Quantity
                      </th>

                      <th className="text-left py-5 text-lg">
                        CO2e
                      </th>

                      <th className="text-left py-5 text-lg">
                        Status
                      </th>

                      <th className="text-left py-5 text-lg">
                        Actions
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {
                      records.map(record => (

                        <tr
                          key={record.id}
                          className="border-b border-white/5 hover:bg-white/5 transition-all duration-300"
                        >

                          <td className="py-6">
                            {record.category}
                          </td>

                          <td>
                            Scope {record.scope}
                          </td>

                          <td>
                            {record.normalized_quantity} {record.normalized_unit}
                          </td>

                          <td>
                            {record.co2e_kg || '-'}
                          </td>

                          <td>

                            <StatusBadge
                              status={record.status}
                            />

                          </td>

                          <td>

                            <div className="flex gap-4">

                              <button
                                onClick={() => approveRecord(record.id)}
                                className="bg-emerald-500/15 text-emerald-300 px-5 py-3 rounded-2xl hover:bg-emerald-500/25 transition-all"
                              >
                                Approve
                              </button>

                              <button
                                onClick={() => rejectRecord(record.id)}
                                className="bg-red-500/15 text-red-300 px-5 py-3 rounded-2xl hover:bg-red-500/25 transition-all"
                              >
                                Reject
                              </button>

                            </div>

                          </td>

                        </tr>

                      ))
                    }

                  </tbody>

                </table>

              </div>

            </div>

          )
        }

        {/* CLIENTS */}

        {
          activeTab === 'clients' && (

            <div className="bg-white/5 border border-white/10 rounded-[32px] p-10 backdrop-blur-xl">

              <h2 className="text-5xl font-black">
                Clients
              </h2>

              <div className="grid grid-cols-3 gap-6 mt-10">

                {
                  clients.map(client => (

                    <div
                      key={client.id}
                      className="bg-[#0b1328] border border-white/10 rounded-3xl p-8"
                    >

                      <h3 className="text-3xl font-bold">
                        {client.name}
                      </h3>

                      <p className="text-slate-400 mt-4">
                        Enterprise ESG Client
                      </p>

                    </div>

                  ))
                }

              </div>

            </div>

          )
        }

        {/* AUDIT */}

        {
          activeTab === 'audit' && (

            <div className="bg-white/5 border border-white/10 rounded-[32px] p-10 backdrop-blur-xl">

              <h2 className="text-5xl font-black">
                Audit Logs
              </h2>

              <div className="space-y-6 mt-10">

                <div className="bg-[#0b1328] rounded-3xl p-8">
                  SAP export validated successfully
                </div>

                <div className="bg-[#0b1328] rounded-3xl p-8">
                  Travel data ingestion completed
                </div>

                <div className="bg-[#0b1328] rounded-3xl p-8">
                  Emission records approved by analyst
                </div>

              </div>

            </div>

          )
        }

        {/* SETTINGS */}

        {
          activeTab === 'settings' && (

            <div className="bg-white/5 border border-white/10 rounded-[32px] p-10 backdrop-blur-xl">

              <h2 className="text-5xl font-black">
                Settings
              </h2>

              <div className="grid grid-cols-2 gap-6 mt-10">

                <div className="bg-[#0b1328] rounded-3xl p-8">
                  API Configuration
                </div>

                <div className="bg-[#0b1328] rounded-3xl p-8">
                  Security Settings
                </div>

              </div>

            </div>

          )
        }

      </div>

    </div>

  )
}

function SidebarItem({
  icon,
  title,
  active,
  onClick
}) {

  return (

    <button
      onClick={onClick}
      className={`w-full flex items-center gap-5 px-6 py-5 rounded-3xl transition-all duration-300
      ${
        active
        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 shadow-2xl'
        : 'hover:bg-white/5'
      }`}
    >

      {icon}

      <span className="font-semibold text-2xl">
        {title}
      </span>

    </button>
  )
}

function StatsCard({ title, value, color, icon }) {

  const colorMap = {
    cyan: 'from-cyan-500/15 to-cyan-400/5 text-cyan-300',
    green: 'from-emerald-500/15 to-emerald-400/5 text-emerald-300',
    yellow: 'from-yellow-500/15 to-yellow-400/5 text-yellow-300',
    red: 'from-red-500/15 to-red-400/5 text-red-300',
  }

  return (

    <div className={`bg-gradient-to-br ${colorMap[color]} border border-white/10 rounded-[32px] p-8`}>

      <div className="flex items-center justify-between">

        <div>

          <p className="text-lg opacity-80">
            {title}
          </p>

          <h2 className="text-6xl font-black mt-5">
            {value}
          </h2>

        </div>

        <div className="bg-white/10 p-5 rounded-3xl">
          {icon}
        </div>

      </div>

    </div>

  )
}

function StatusBadge({ status }) {

  if (status === 'approved') {

    return (
      <div className="bg-emerald-500/15 text-emerald-300 px-5 py-3 rounded-full inline-block">
        Approved
      </div>
    )
  }

  if (status === 'rejected') {

    return (
      <div className="bg-red-500/15 text-red-300 px-5 py-3 rounded-full inline-block">
        Rejected
      </div>
    )
  }

  if (status === 'suspicious') {

    return (
      <div className="bg-yellow-500/15 text-yellow-300 px-5 py-3 rounded-full inline-block">
        Suspicious
      </div>
    )
  }

  return (
    <div className="bg-slate-500/15 text-slate-300 px-5 py-3 rounded-full inline-block">
      Pending
    </div>
  )
}

export default App