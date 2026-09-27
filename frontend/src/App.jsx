import { useRef, useState } from 'react'
import {
  AlertTriangle,
  ArrowUpRight,
  BriefcaseBusiness,
  ChevronRight,
  Download,
  FileText,
  Landmark,
  LayoutDashboard,
  LoaderCircle,
  Menu,
  Percent,
  ShieldCheck,
  TrendingUp,
  Upload,
  WalletCards,
  X,
} from 'lucide-react'
import { calculateTax, getAnalysis, getExportReport, getProfiles, getReview, uploadCsv } from './services/api'

const formatAmount = (value) => `Rs ${Number(value || 0).toLocaleString('en-IN')}`

const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'risk', label: 'Risk Center', icon: ShieldCheck },
  { id: 'tax', label: 'Tax', icon: Percent },
  { id: 'reports', label: 'Reports', icon: FileText },
]

const taxSections = [
  { id: 'types', label: 'Types' },
  { id: 'regime', label: 'Regime' },
  { id: 'income', label: 'Income' },
  { id: 'deductions', label: 'Deductions' },
  { id: 'loans', label: 'Loans' },
  { id: 'investments', label: 'Investments' },
  { id: 'tax-calculation', label: 'Tax Calculation' },
]

function App() {
  const fileInput = useRef(null)
  const [analysis, setAnalysis] = useState(null)
  const [profiles, setProfiles] = useState(null)
  const [review, setReview] = useState({ cases: [], count: 0 })
  const [activeTab, setActiveTab] = useState('dashboard')
  const [taxSection, setTaxSection] = useState('regime')
  const [selectedRegime, setSelectedRegime] = useState('compare')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [filename, setFilename] = useState('')
  const [status, setStatus] = useState('Upload a CSV bank statement to begin.')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [taxForm, setTaxForm] = useState({
    assessmentYear: '2026-27',
    age: 35,
    residentialStatus: 'resident',
    employmentType: 'salaried',
    basicSalary: 1200000,
    annualIncome: 1200000,
    annualExpenses: 350000,
    annualInvestments: 120000,
    loanEMI: 25000,
    section80C: 150000,
    section80D: 25000,
    tds: 0,
  })
  const [taxResult, setTaxResult] = useState(null)
  const [taxLoading, setTaxLoading] = useState(false)
  const [taxError, setTaxError] = useState('')

  async function refreshProfileData() {
    const [profileResult, reviewResult] = await Promise.all([getProfiles(), getReview()])
    setProfiles(profileResult)
    setReview(reviewResult)
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    setError('')
    setFilename(file.name)
    setStatus('Validating your transactions...')

    try {
      await uploadCsv(file)
      setStatus('CSV validated. Running transparent analysis rules...')
      const result = await getAnalysis()
      setAnalysis(result)
      await refreshProfileData()
      setStatus('Analysis complete. Review the risk, evidence, and recommendations below.')
    } catch (uploadError) {
      setError(uploadError.message)
      setStatus('The file could not be analyzed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleExport() {
    try {
      const payload = await getExportReport()
      const blob = new Blob([payload.content], { type: payload.mime_type || 'text/plain' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = payload.filename || 'taxsaarthi_report.txt'
      link.click()
      URL.revokeObjectURL(url)
      setStatus('Report downloaded as a plain-text export.')
    } catch (exportError) {
      setError(exportError.message)
    }
  }

  async function handleTaxCalculate(event) {
    event.preventDefault()
    setTaxLoading(true)
    setTaxError('')

    try {
      const payload = {
        assessmentYear: taxForm.assessmentYear,
        age: Number(taxForm.age || 0),
        residentialStatus: taxForm.residentialStatus,
        employmentType: taxForm.employmentType,
        salary: { basicSalary: Number(taxForm.basicSalary || 0) },
        financialProfile: {
          annualIncome: Number(taxForm.annualIncome || 0),
          annualExpenses: Number(taxForm.annualExpenses || 0),
          annualInvestments: Number(taxForm.annualInvestments || 0),
          loanEMI: Number(taxForm.loanEMI || 0),
        },
        deductions: {
          section80C: Number(taxForm.section80C || 0),
          section80D: Number(taxForm.section80D || 0),
        },
        tds: Number(taxForm.tds || 0),
      }

      const result = await calculateTax(payload)
      setTaxResult(result)
      setStatus('Tax engine has calculated the Old vs New regime estimate.')
    } catch (taxErrorCaught) {
      setTaxError(taxErrorCaught.message)
    } finally {
      setTaxLoading(false)
    }
  }

  const summary = analysis?.summary
  const risk = analysis?.risk
  const findings = analysis?.findings || []
  const aiInsights = analysis?.ai_insights || []
  const expertKnowledge = analysis?.expert_knowledge || []
  const report = analysis?.report
  const loanProfile = profiles?.loan_profile || {}
  const investmentProfile = profiles?.investment_profile || {}

  const renderTaxFieldBlock = () => {
    switch (taxSection) {
      case 'types':
        return (
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-600">
              Assessment Year
              <select value={taxForm.assessmentYear} onChange={(e) => setTaxForm({ ...taxForm, assessmentYear: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2">
                <option value="2026-27">2026-27</option>
              </select>
            </label>
            <label className="text-sm text-slate-600">
              Age
              <input type="number" value={taxForm.age} onChange={(e) => setTaxForm({ ...taxForm, age: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <label className="text-sm text-slate-600">
              Residential status
              <select value={taxForm.residentialStatus} onChange={(e) => setTaxForm({ ...taxForm, residentialStatus: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2">
                <option value="resident">Resident</option>
                <option value="non-resident">Non-resident</option>
              </select>
            </label>
            <label className="text-sm text-slate-600">
              Employment type
              <select value={taxForm.employmentType} onChange={(e) => setTaxForm({ ...taxForm, employmentType: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2">
                <option value="salaried">Salaried</option>
                <option value="freelancer">Freelancer</option>
                <option value="business">Business</option>
                <option value="professional">Professional</option>
              </select>
            </label>
          </div>
        )
      case 'regime':
        return (
          <div className="space-y-4">
            <label className="block text-sm text-slate-600">
              Regime selection
              <select value={selectedRegime} onChange={(e) => setSelectedRegime(e.target.value)} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2">
                <option value="compare">Compare both</option>
                <option value="oldRegime">Old regime</option>
                <option value="newRegime">New regime</option>
              </select>
            </label>
            {taxResult && (
              <div className="grid gap-3 sm:grid-cols-2">
                <div className={`rounded-xl p-4 ${selectedRegime === 'oldRegime' ? 'bg-[#edf8f4] ring-2 ring-[#176b5b]' : 'bg-[#f5f7f6]'}`}>
                  <p className="text-slate-500">Old Regime</p>
                  <p className="mt-1 text-2xl font-bold text-[#176b5b]">Rs {Number(taxResult.oldRegime.totalTax || 0).toLocaleString('en-IN')}</p>
                </div>
                <div className={`rounded-xl p-4 ${selectedRegime === 'newRegime' ? 'bg-[#edf8f4] ring-2 ring-[#176b5b]' : 'bg-[#f5f7f6]'}`}>
                  <p className="text-slate-500">New Regime</p>
                  <p className="mt-1 text-2xl font-bold text-[#176b5b]">Rs {Number(taxResult.newRegime.totalTax || 0).toLocaleString('en-IN')}</p>
                </div>
              </div>
            )}
          </div>
        )
      case 'income':
        return (
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-600 md:col-span-2">
              Basic salary
              <input type="number" value={taxForm.basicSalary} onChange={(e) => setTaxForm({ ...taxForm, basicSalary: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <label className="text-sm text-slate-600">
              Annual income
              <input type="number" value={taxForm.annualIncome} onChange={(e) => setTaxForm({ ...taxForm, annualIncome: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <label className="text-sm text-slate-600">
              Annual expenses
              <input type="number" value={taxForm.annualExpenses} onChange={(e) => setTaxForm({ ...taxForm, annualExpenses: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
          </div>
        )
      case 'deductions':
        return (
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-600">
              80C deductions
              <input type="number" value={taxForm.section80C} onChange={(e) => setTaxForm({ ...taxForm, section80C: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <label className="text-sm text-slate-600">
              80D deductions
              <input type="number" value={taxForm.section80D} onChange={(e) => setTaxForm({ ...taxForm, section80D: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <label className="text-sm text-slate-600 md:col-span-2">
              TDS already paid
              <input type="number" value={taxForm.tds} onChange={(e) => setTaxForm({ ...taxForm, tds: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
          </div>
        )
      case 'loans':
        return (
          <div className="space-y-4">
            <label className="text-sm text-slate-600">
              Loan EMI (annual)
              <input type="number" value={taxForm.loanEMI} onChange={(e) => setTaxForm({ ...taxForm, loanEMI: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <div className="rounded-xl bg-[#edf8f4] p-4 text-sm text-slate-600">
              Debt servicing should be reviewed alongside your savings rate and investment capacity.
            </div>
          </div>
        )
      case 'investments':
        return (
          <div className="space-y-4">
            <label className="text-sm text-slate-600">
              Annual investments
              <input type="number" value={taxForm.annualInvestments} onChange={(e) => setTaxForm({ ...taxForm, annualInvestments: e.target.value })} className="mt-1 w-full rounded-xl border border-[#dbe4d9] bg-white px-3 py-2" />
            </label>
            <div className="rounded-xl bg-[#f5f7f6] p-4 text-sm text-slate-600">
              Investment proof and product-level rules are required for deduction eligibility and tax planning review.
            </div>
          </div>
        )
      case 'tax-calculation':
      default:
        return (
          <div className="space-y-4">
            <div className="rounded-xl bg-[#fff3d8] p-4 text-sm text-[#73561e]">
              Enter taxpayer details and click Calculate tax to compare the Old and New tax regimes.
            </div>
            <div className="rounded-xl border border-[#dbe4d9] bg-white p-4 text-sm text-slate-600">
              <div className="flex items-center justify-between"><span className="font-semibold text-[#176b5b]">Current selection</span><span className="rounded bg-[#edf8f4] px-2 py-1 text-xs font-medium text-[#176b5b]">{selectedRegime === 'compare' ? 'Compare both' : selectedRegime}</span></div>
              {taxResult && (
                <div className="mt-3 space-y-2">
                  <p>Difference: <span className="font-semibold">Rs {Number(taxResult.comparison?.difference || 0).toLocaleString('en-IN')}</span></p>
                  <p>Warnings: <span className="font-semibold">{(taxResult.warnings && taxResult.warnings.length) ? taxResult.warnings.join(', ') : 'None'}</span></p>
                </div>
              )}
            </div>
          </div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-[#f4f7f2] text-[#17212b]">
      <aside className={`${sidebarOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0 lg:w-20'} fixed left-0 top-0 z-30 h-screen border-r border-[#dbe4d9] bg-[#fbfcf8] p-4 transition-all duration-200 lg:block`}>
        <div className="flex items-center justify-between gap-3">
          <div className={`flex items-center gap-3 text-xl font-bold text-[#176b5b] ${!sidebarOpen && 'lg:justify-center'}`}>
            <WalletCards size={25} />
            {sidebarOpen && <span>TaxSaarthi</span>}
          </div>
          <button type="button" onClick={() => setSidebarOpen(!sidebarOpen)} className="rounded-lg border border-[#dbe4d9] bg-white p-2 text-slate-600 lg:hidden">
            {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        {sidebarOpen && <p className="mt-2 text-sm text-slate-500">Financial clarity, one statement at a time.</p>}

        <nav className="mt-8 space-y-2 text-sm font-semibold">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 ${activeTab === id ? 'bg-[#dcefe8] text-[#176b5b]' : 'text-slate-500 hover:bg-[#eef3ec]'}`}
            >
              <Icon size={18} />
              {sidebarOpen && <span>{label}</span>}
            </button>
          ))}
        </nav>

        {activeTab === 'tax' && sidebarOpen && (
          <div className="mt-6 rounded-2xl border border-[#dbe4d9] bg-[#eef3ec] p-3">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Tax sections</p>
            <div className="space-y-1">
              {taxSections.map((section) => (
                <button
                  key={section.id}
                  type="button"
                  onClick={() => setTaxSection(section.id)}
                  className={`flex w-full items-center justify-between rounded-lg px-2 py-2 text-left text-sm ${taxSection === section.id ? 'bg-white font-semibold text-[#176b5b]' : 'text-slate-600 hover:bg-white/60'}`}
                >
                  <span>{section.label}</span>
                  <ChevronRight size={14} />
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="absolute bottom-6 left-6 right-6 rounded-xl bg-[#fff3d8] p-4 text-xs leading-5 text-[#73561e]">
          {sidebarOpen ? 'Informational prototype. Verify findings before making financial or tax decisions.' : 'Prototype'}
        </div>
      </aside>

      <main className={`${sidebarOpen ? 'lg:ml-72' : 'lg:ml-20'} transition-all duration-200`}>
        <header className="border-b border-[#dbe4d9] bg-[#fbfcf8] px-6 py-5 lg:px-10">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#176b5b]">Decision support workspace</p>
              <h1 className="mt-2 text-3xl font-bold tracking-tight">Your financial overview</h1>
              <p className="mt-1 text-slate-500">Explainable financial intelligence for cash-flow, debt, and tax clarity.</p>
            </div>
            <button type="button" onClick={() => setSidebarOpen(!sidebarOpen)} className="rounded-xl border border-[#dbe4d9] bg-white p-2 text-slate-600 lg:hidden">
              {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </header>

        <section className="p-6 lg:p-10">
          <div className="rounded-2xl bg-[#176b5b] p-6 text-white shadow-sm lg:flex lg:items-center lg:justify-between">
            <div>
              <h2 className="text-xl font-bold">Analyze a statement</h2>
              <p className="mt-1 max-w-xl text-sm text-emerald-50">Upload CSV files with date, description, amount, and type columns.</p>
            </div>
            <div className="flex items-center gap-3">
              {analysis && (
                <button onClick={handleExport} className="mt-5 flex items-center gap-2 rounded-xl border border-white/30 bg-white/10 px-4 py-3 font-semibold text-white transition hover:bg-white/20 lg:mt-0">
                  <Download size={18} /> Export report
                </button>
              )}
              <button onClick={() => fileInput.current?.click()} className="mt-5 flex items-center gap-2 rounded-xl bg-[#f2c14e] px-5 py-3 font-bold text-[#17212b] transition hover:bg-[#ffd66f] lg:mt-0">
                <Upload size={18} /> {loading ? 'Analyzing...' : 'Upload CSV'}
              </button>
            </div>
            <input ref={fileInput} type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
          </div>

          <div className="mt-4 text-sm text-slate-600">{filename && `Selected: ${filename} · `}{status}</div>
          {error && <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

          {!analysis && !loading && (
            <div className="mt-10 rounded-2xl border border-dashed border-[#b9cbb9] bg-[#fbfcf8] p-12 text-center">
              <FileText className="mx-auto text-[#176b5b]" size={42} />
              <h2 className="mt-4 text-xl font-bold">No statement analyzed yet</h2>
              <p className="mt-2 text-slate-500">Use the sample file in <span className="font-semibold">backend/sample_data</span> to see the dashboard in action.</p>
            </div>
          )}

          {loading && (
            <div className="mt-10 flex items-center justify-center gap-3 rounded-2xl bg-[#fbfcf8] p-12 text-slate-600">
              <LoaderCircle className="animate-spin" /> Processing your statement...
            </div>
          )}

          {analysis && (
            <>
              {activeTab === 'dashboard' && (
                <>
                  <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    {[
                      ['Total income', summary.total_income, 'text-[#176b5b]'],
                      ['Total expenses', summary.total_expenses, 'text-[#b5533f]'],
                      ['Net savings', summary.net_savings, 'text-[#176b5b]'],
                      ['Transactions', summary.transaction_count, 'text-[#73561e]'],
                    ].map(([label, value, color]) => (
                      <div key={label} className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-5">
                        <p className="text-sm text-slate-500">{label}</p>
                        <p className={`mt-3 text-2xl font-bold ${color}`}>
                          {label === 'Transactions' ? value : formatAmount(value)}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-8 grid gap-6 xl:grid-cols-3">
                    <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6 xl:col-span-2">
                      <div className="flex items-center justify-between">
                        <h2 className="text-lg font-bold">Expense categories</h2>
                        <ArrowUpRight className="text-[#176b5b]" size={20} />
                      </div>
                      <div className="mt-5 space-y-4">
                        {analysis.category_breakdown.map((item) => (
                          <div key={item.category}>
                            <div className="flex justify-between text-sm">
                              <span>{item.category}</span>
                              <span className="font-semibold">{formatAmount(item.amount)}</span>
                            </div>
                            <div className="mt-2 h-2 rounded-full bg-[#e4ebe1]">
                              <div
                                className="h-2 rounded-full bg-[#176b5b]"
                                style={{ width: `${Math.min((item.amount / Math.max(summary.total_expenses, 1)) * 100, 100)}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>

                    <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="text-[#176b5b]" size={18} />
                        <h2 className="text-lg font-bold">Risk snapshot</h2>
                      </div>
                      <div className="mt-5 rounded-xl bg-[#edf8f4] p-4">
                        <p className="text-sm text-slate-500">Overall risk</p>
                        <p className="mt-2 text-2xl font-bold text-[#176b5b] uppercase">{risk?.level || 'low'}</p>
                        <p className="mt-2 text-sm text-slate-600">{risk?.summary}</p>
                      </div>
                      <div className="mt-4 text-sm text-slate-600">
                        <p>Risk score: <span className="font-semibold">{risk?.score || 0}/100</span></p>
                        <p className="mt-2">Narrative: {analysis.narrative}</p>
                      </div>
                    </section>
                  </div>

                  <div className="mt-8 grid gap-6 xl:grid-cols-2">
                    <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                      <h2 className="text-lg font-bold">Key findings</h2>
                      <div className="mt-4 space-y-3">
                        {findings.length === 0 && <p className="text-sm text-slate-500">No major findings were triggered by the current dataset.</p>}
                        {findings.map((finding, index) => (
                          <div key={`${finding.title}-${index}`} className="rounded-xl bg-[#fff3d8] p-4">
                            <div className="flex gap-3">
                              <AlertTriangle className="mt-0.5 shrink-0 text-[#b27b14]" size={18} />
                              <div>
                                <p className="font-semibold">{finding.title}</p>
                                <p className="mt-1 text-sm text-slate-600">{finding.what_happened}</p>
                                <p className="mt-2 text-xs text-slate-500">Why it matters: {finding.why_it_matters}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>

                    <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                      <h2 className="text-lg font-bold">AI + expert insight</h2>
                      <div className="mt-4 space-y-3">
                        {aiInsights.map((insight, index) => (
                          <div key={`${insight.title}-${index}`} className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                            <p className="font-semibold">{insight.title}</p>
                            <p className="mt-1 text-sm text-slate-600">{insight.summary}</p>
                            <p className="mt-2 text-xs text-slate-500">Confidence: {insight.confidence}</p>
                          </div>
                        ))}
                        {expertKnowledge.length === 0 && aiInsights.length === 0 && (
                          <p className="text-sm text-slate-500">No expert rule patterns were triggered.</p>
                        )}
                      </div>
                    </section>
                  </div>
                </>
              )}

              {activeTab === 'risk' && (
                <div className="mt-8 grid gap-6 xl:grid-cols-2">
                  <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="text-[#176b5b]" size={18} />
                      <h2 className="text-lg font-bold">Risk center</h2>
                    </div>
                    <div className="mt-5 rounded-xl bg-[#edf8f4] p-5">
                      <p className="text-sm text-slate-500">Current risk level</p>
                      <p className="mt-2 text-3xl font-bold text-[#176b5b] uppercase">{risk?.level || 'low'}</p>
                      <p className="mt-3 text-sm text-slate-600">{risk?.summary}</p>
                    </div>
                    <div className="mt-5 text-sm text-slate-600">
                      <p>Risk score: <span className="font-semibold">{risk?.score || 0}/100</span></p>
                      <p className="mt-2">Savings rate: <span className="font-semibold">{summary?.net_savings ? ((summary.net_savings / Math.max(summary.total_income, 1)) * 100).toFixed(1) : 0}%</span></p>
                    </div>
                  </section>

                  <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                    <h2 className="text-lg font-bold">Rule and expert triggers</h2>
                    <div className="mt-4 space-y-3">
                      {analysis.rule_hits.map((rule, index) => (
                        <div key={`${rule.id}-${index}`} className="rounded-xl bg-[#eef3ec] p-4">
                          <p className="font-semibold">{rule.id}: {rule.name}</p>
                          <p className="mt-1 text-sm text-slate-600">{rule.result}</p>
                        </div>
                      ))}
                      {expertKnowledge.map((expert, index) => (
                        <div key={`${expert.title}-${index}`} className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                          <p className="font-semibold">{expert.title}</p>
                          <p className="mt-1 text-sm text-slate-600">{expert.summary}</p>
                        </div>
                      ))}
                      {analysis.rule_hits.length === 0 && expertKnowledge.length === 0 && (
                        <p className="text-sm text-slate-500">No major rule triggers were detected.</p>
                      )}
                    </div>
                  </section>

                  <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6 xl:col-span-2">
                    <h2 className="text-lg font-bold">Human review cases</h2>
                    <div className="mt-4 space-y-3">
                      {review.cases.map((caseItem) => (
                        <div key={caseItem.case_id} className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                          <div className="flex items-center justify-between gap-3">
                            <p className="font-semibold">{caseItem.case_id} · {caseItem.title}</p>
                            <span className="rounded-full bg-[#fff3d8] px-2 py-1 text-xs font-semibold uppercase text-[#73561e]">{caseItem.severity}</span>
                          </div>
                          <p className="mt-2 text-sm text-slate-600">{caseItem.summary}</p>
                          <p className="mt-2 text-xs text-slate-500">Recommended action: {caseItem.recommended_action}</p>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
              )}

              {activeTab === 'tax' && (
                <div className="mt-8 grid gap-6 xl:grid-cols-[280px,1fr]">
                  <aside className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-4">
                    <div className="mb-3 flex items-center gap-2">
                      <Percent className="text-[#176b5b]" size={18} />
                      <h2 className="text-lg font-bold">Tax planner</h2>
                    </div>
                    <div className="space-y-2">
                      {taxSections.map((section) => (
                        <button
                          key={section.id}
                          type="button"
                          onClick={() => setTaxSection(section.id)}
                          className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm ${taxSection === section.id ? 'bg-[#dcefe8] font-semibold text-[#176b5b]' : 'text-slate-600 hover:bg-[#eef3ec]'}`}
                        >
                          <span>{section.label}</span>
                          <ChevronRight size={14} />
                        </button>
                      ))}
                    </div>
                  </aside>

                  <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2">
                        <Percent className="text-[#176b5b]" size={18} />
                        <h2 className="text-lg font-bold">Tax calculation</h2>
                      </div>
                      <span className="rounded-full bg-[#edf8f4] px-3 py-1 text-xs font-semibold uppercase text-[#176b5b]">{taxSections.find((s) => s.id === taxSection)?.label || 'Tax'}</span>
                    </div>

                    <form className="mt-5 space-y-6" onSubmit={handleTaxCalculate}>
                      {renderTaxFieldBlock()}

                      <div className="flex flex-wrap gap-3">
                        <button type="submit" disabled={taxLoading} className="rounded-xl bg-[#176b5b] px-4 py-3 font-semibold text-white disabled:opacity-60">
                          {taxLoading ? 'Calculating...' : 'Calculate tax'}
                        </button>
                        <button type="button" onClick={() => setTaxSection('regime')} className="rounded-xl border border-[#dbe4d9] bg-white px-4 py-3 font-semibold text-slate-600">
                          Regime summary
                        </button>
                      </div>
                    </form>

                    {taxError && <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{taxError}</div>}

                    {!taxResult && (
                      <div className="mt-5 rounded-xl bg-[#fff3d8] p-4 text-sm text-[#73561e]">
                        Enter taxpayer details and click Calculate tax to compare the Old and New tax regimes.
                      </div>
                    )}

                    {taxResult && (
                      <div className="mt-6 space-y-4 text-sm text-slate-600">
                        <div className="grid gap-3 sm:grid-cols-2">
                          <div className={`rounded-xl p-4 ${selectedRegime === 'oldRegime' ? 'bg-[#edf8f4] ring-2 ring-[#176b5b]' : 'bg-[#f5f7f6]'}`}>
                            <p className="text-slate-500">Old Regime</p>
                            <p className="mt-1 text-2xl font-bold text-[#176b5b]">Rs {Number(taxResult.oldRegime.totalTax || 0).toLocaleString('en-IN')}</p>
                          </div>
                          <div className={`rounded-xl p-4 ${selectedRegime === 'newRegime' ? 'bg-[#edf8f4] ring-2 ring-[#176b5b]' : 'bg-[#f5f7f6]'}`}>
                            <p className="text-slate-500">New Regime</p>
                            <p className="mt-1 text-2xl font-bold text-[#176b5b]">Rs {Number(taxResult.newRegime.totalTax || 0).toLocaleString('en-IN')}</p>
                          </div>
                        </div>

                        <div className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                          <p className="font-semibold text-[#176b5b]">Financial health snapshot</p>
                          <div className="mt-3 grid gap-2 sm:grid-cols-2">
                            <div><span className="text-slate-500">Income:</span> <span className="font-semibold">Rs {Number(taxResult.financialSummary?.totalIncome || 0).toLocaleString('en-IN')}</span></div>
                            <div><span className="text-slate-500">Expenses:</span> <span className="font-semibold">Rs {Number(taxResult.financialSummary?.totalExpenses || 0).toLocaleString('en-IN')}</span></div>
                            <div><span className="text-slate-500">Net cash flow:</span> <span className="font-semibold">Rs {Number(taxResult.financialSummary?.availableCashFlow || 0).toLocaleString('en-IN')}</span></div>
                            <div><span className="text-slate-500">Savings rate:</span> <span className="font-semibold">{Number(taxResult.financialSummary?.savingsRate || 0).toFixed(1)}%</span></div>
                          </div>
                        </div>

                        <div className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                          <p className="font-semibold text-[#176b5b]">Section 87A rebate</p>
                          <div className="mt-3 space-y-2">
                            <div>Eligibility: <span className="font-semibold">{taxResult.newRegime?.rebate87A > 0 ? 'Eligible' : 'Not eligible'}</span></div>
                            <div>Threshold: <span className="font-semibold">Rs {Number(1200000).toLocaleString('en-IN')}</span></div>
                            <div>Actual rebate applied: <span className="font-semibold">Rs {Number(taxResult.newRegime?.rebate87A || 0).toLocaleString('en-IN')}</span></div>
                          </div>
                        </div>

                        <div className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                          <p className="font-semibold text-[#176b5b]">Audit trail</p>
                          <div className="mt-3 space-y-2">
                            {(taxResult.auditTrail || []).slice(0, 4).map((step, index) => (
                              <div key={`${step.step}-${index}`} className="rounded-lg bg-[#f5f7f6] p-2 text-xs text-slate-600">
                                <span className="font-semibold">{step.step}</span> · {step.reason || step.message || 'Rule applied'}
                              </div>
                            ))}
                          </div>
                        </div>

                        <p>Difference: <span className="font-semibold">Rs {Number(taxResult.comparison?.difference || 0).toLocaleString('en-IN')}</span></p>
                        <p>Warnings: <span className="font-semibold">{(taxResult.warnings && taxResult.warnings.length) ? taxResult.warnings.join(', ') : 'None'}</span></p>
                        <p>Rules used: <span className="font-semibold">{taxResult.rulesApplied?.join(', ') || 'Not available'}</span></p>
                      </div>
                    )}
                  </section>
                </div>
              )}

              {activeTab === 'reports' && (
                <div className="mt-8 grid gap-6 xl:grid-cols-2">
                  <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                    <div className="flex items-center gap-2">
                      <BriefcaseBusiness className="text-[#176b5b]" size={18} />
                      <h2 className="text-lg font-bold">Loan and investment profile</h2>
                    </div>
                    <div className="mt-5 space-y-4 text-sm text-slate-600">
                      <div className="rounded-xl bg-[#edf8f4] p-4">
                        <div className="flex items-center gap-2"><Landmark size={16} className="text-[#176b5b]" /> <span className="font-semibold">Loan profile</span></div>
                        <p className="mt-2">Monthly EMI: <span className="font-semibold">{formatAmount(loanProfile.monthly_emi || 0)}</span></p>
                        <p>Debt-to-income ratio: <span className="font-semibold">{loanProfile.debt_to_income_ratio || 0}%</span></p>
                        <p className="mt-2 text-xs text-slate-500">{loanProfile.recommended_action}</p>
                      </div>
                      <div className="rounded-xl border border-[#dbe4d9] bg-white p-4">
                        <div className="flex items-center gap-2"><TrendingUp size={16} className="text-[#176b5b]" /> <span className="font-semibold">Investment profile</span></div>
                        <p className="mt-2">Monthly investment: <span className="font-semibold">{formatAmount(investmentProfile.monthly_investment || 0)}</span></p>
                        <div className="mt-2 text-xs text-slate-500">
                          {Object.entries(investmentProfile.asset_allocation || {}).map(([key, value]) => (
                            <div key={key} className="mt-1">{key}: {formatAmount(value)}</div>
                          ))}
                        </div>
                        <p className="mt-2 text-xs text-slate-500">{investmentProfile.recommended_action}</p>
                      </div>
                    </div>
                  </section>

                  <section className="rounded-2xl border border-[#dbe4d9] bg-[#fbfcf8] p-6">
                    <h2 className="text-lg font-bold">Executive report</h2>
                    {report ? (
                      <>
                        <p className="mt-4 text-slate-600">{report.executive_summary}</p>
                        <div className="mt-4 grid gap-3">
                          {report.recommendations.map((recommendation, index) => (
                            <div key={`${recommendation}-${index}`} className="rounded-xl bg-[#edf8f4] p-4 text-sm text-slate-700">
                              {recommendation}
                            </div>
                          ))}
                        </div>
                      </>
                    ) : (
                      <p className="mt-4 text-sm text-slate-500">No report is available until the analysis has been completed.</p>
                    )}
                  </section>
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
