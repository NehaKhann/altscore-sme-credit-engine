import { useState } from 'react';
import { createBusiness } from '../services/api';
import type { BusinessRequest, BusinessResponse, LoanMatch } from '../services/api';
import ChatAssistant from '../components/ChatAssistant';

export default function SubmitBusiness() {
  const [form, setForm] = useState<BusinessRequest>({
    businessName: '',
    ownerName: '',
    businessType: '',
    monthlyRevenue: 0,
    yearsInOperation: 0,
    numTransactions: 0,
  });
  const [result, setResult] = useState<BusinessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'explanation' | 'recommendations' | 'loans'>('loans');

  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await createBusiness(form);
      setResult(res.data);
      setActiveTab('loans');
    } catch (e) {
      setError('Failed to submit. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' };
      case 'MEDIUM': return { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-300' };
      case 'HIGH': return { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' };
      case 'VERY_HIGH': return { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' };
      default: return { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' };
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const getLoanStatusConfig = (status: LoanMatch['matchStatus']) => {
    switch (status) {
      case 'QUALIFIED':
        return {
          badge: 'bg-green-100 text-green-700 border border-green-300',
          label: '✅ Qualified',
          cardBorder: 'border-green-200 bg-green-50/30'
        };
      case 'ALMOST':
        return {
          badge: 'bg-yellow-100 text-yellow-700 border border-yellow-300',
          label: '⚠️ Almost There',
          cardBorder: 'border-yellow-200 bg-yellow-50/30'
        };
      default:
        return {
          badge: 'bg-gray-100 text-gray-500 border border-gray-200',
          label: '❌ Not Yet',
          cardBorder: 'border-gray-200 bg-gray-50/30'
        };
    }
  };

  const scorePercent = result ? result.creditScore : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">

      {/* Header */}
      <div className="bg-white border-b shadow-sm px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-indigo-700">AltScore</h1>
            <p className="text-xs text-gray-400">AI-Powered SME Credit Engine • Saudi Arabia</p>
          </div>
          <div className="flex items-center gap-4">
            {result && (
              <button
                onClick={() => setResult(null)}
                className="text-sm text-indigo-600 border border-indigo-200 px-4 py-2 rounded-lg hover:bg-indigo-50"
              >
                New Application
              </button>
            )}
            <div className="flex items-center gap-3 border-l pl-4">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                <span className="text-indigo-600 text-xs font-bold">
                  {user.fullName?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <span className="text-sm text-gray-600 hidden sm:inline">{user.fullName || user.email}</span>
              <button
                onClick={handleLogout}
                className="text-sm bg-gray-100 text-gray-600 px-3 py-1.5 rounded-lg hover:bg-red-50 hover:text-red-600 transition"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6">

        {/* Form */}
        {!result && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8 mt-4">
              <h2 className="text-3xl font-bold text-gray-800">Get Your Credit Score</h2>
              <p className="text-gray-500 mt-2">See which KSA banks you qualify for — instantly</p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Business Name</label>
                  <input
                    className="w-full border border-gray-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    placeholder="e.g. Ahmed's Grocery"
                    value={form.businessName}
                    onChange={e => setForm({ ...form, businessName: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Owner Name</label>
                  <input
                    className="w-full border border-gray-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    placeholder="e.g. Ahmed Ali"
                    value={form.ownerName}
                    onChange={e => setForm({ ...form, ownerName: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Business Type</label>
                  <select
                    className="w-full border border-gray-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    value={form.businessType}
                    onChange={e => setForm({ ...form, businessType: e.target.value })}
                  >
                    <option value="">Select type</option>
                    <option value="RETAIL">Retail</option>
                    <option value="FOOD">Food & Beverage</option>
                    <option value="SERVICE">Service</option>
                    <option value="MANUFACTURING">Manufacturing</option>
                    <option value="TECH">Technology</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Monthly Revenue (SAR)</label>
                  <input
                    type="number"
                    className="w-full border border-gray-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    placeholder="e.g. 25000"
                    value={form.monthlyRevenue || ''}
                    onChange={e => setForm({ ...form, monthlyRevenue: Number(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Years in Operation</label>
                  <input
                    type="number"
                    className="w-full border border-gray-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    placeholder="e.g. 3"
                    value={form.yearsInOperation || ''}
                    onChange={e => setForm({ ...form, yearsInOperation: Number(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Monthly Transactions</label>
                  <input
                    type="number"
                    className="w-full border border-gray-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                    placeholder="e.g. 60"
                    value={form.numTransactions || ''}
                    onChange={e => setForm({ ...form, numTransactions: Number(e.target.value) })}
                  />
                </div>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                  {error}
                </div>
              )}

              <button
                onClick={handleSubmit}
                disabled={loading}
                className="mt-6 w-full bg-indigo-600 text-white py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Analyzing with AI...
                  </span>
                ) : 'Get Credit Score & Loan Matches'}
              </button>
            </div>
          </div>
        )}

        {/* Results Dashboard */}
        {result && (
          <div className="space-y-6">

            {/* Top Stats Row */}
            <div className="grid grid-cols-4 gap-4">

              {/* Score Card */}
              <div className="bg-white rounded-2xl shadow p-6 flex flex-col items-center justify-center">
                <p className="text-sm text-gray-500 mb-2">Credit Score</p>
                <div className="relative w-24 h-24">
                  <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="15.9" fill="none"
                      stroke={scorePercent >= 80 ? '#16a34a' : scorePercent >= 60 ? '#ca8a04' : scorePercent >= 40 ? '#ea580c' : '#dc2626'}
                      strokeWidth="3"
                      strokeDasharray={`${scorePercent} 100`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-2xl font-bold ${getScoreColor(result.creditScore)}`}>
                      {result.creditScore}
                    </span>
                    <span className="text-xs text-gray-400">/100</span>
                  </div>
                </div>
                <p className={`mt-2 font-semibold text-sm ${getScoreColor(result.creditScore)}`}>
                  {getScoreLabel(result.creditScore)}
                </p>
              </div>

              {/* Risk Level */}
              <div className="bg-white rounded-2xl shadow p-6 flex flex-col items-center justify-center">
                <p className="text-sm text-gray-500 mb-3">Risk Level</p>
                <span className={`px-4 py-2 rounded-full font-bold text-sm border ${getRiskColor(result.riskLevel).bg} ${getRiskColor(result.riskLevel).text} ${getRiskColor(result.riskLevel).border}`}>
                  {result.riskLevel}
                </span>
                <p className="text-xs text-gray-400 mt-3 text-center">{result.businessName}</p>
                <p className="text-xs text-gray-400">{result.businessType}</p>
              </div>

              {/* Qualified Banks */}
              <div className="bg-white rounded-2xl shadow p-6 flex flex-col items-center justify-center">
                <p className="text-sm text-gray-500 mb-2">Banks Qualified</p>
                <p className="text-5xl font-bold text-green-600">{result.qualifiedLoansCount}</p>
                <p className="text-xs text-gray-400 mt-2">out of 8 programs</p>
              </div>

              {/* Almost Banks */}
              <div className="bg-white rounded-2xl shadow p-6 flex flex-col items-center justify-center">
                <p className="text-sm text-gray-500 mb-2">Almost Qualifying</p>
                <p className="text-5xl font-bold text-yellow-500">{result.almostLoansCount}</p>
                <p className="text-xs text-gray-400 mt-2">more banks close</p>
              </div>
            </div>

            {/* Business Stats */}
            <div className="bg-white rounded-2xl shadow p-5">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-800">
                    SAR {result.monthlyRevenue.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Monthly Revenue</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-800">
                    {result.yearsInOperation} yr{result.yearsInOperation !== 1 ? 's' : ''}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">In Operation</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-800">{result.numTransactions}</p>
                  <p className="text-xs text-gray-500 mt-1">Monthly Transactions</p>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-2xl shadow overflow-hidden">
              <div className="flex border-b">
                {[
                  { key: 'loans', label: `🏦 Loan Matches (${result.qualifiedLoansCount} qualified)` },
                  { key: 'explanation', label: '🤖 AI Explanation' },
                  { key: 'recommendations', label: '📈 Recommendations' },
                ].map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as typeof activeTab)}
                    className={`flex-1 py-4 font-semibold text-sm transition ${
                      activeTab === tab.key
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="p-6">

                {/* Loan Matches Tab */}
                {activeTab === 'loans' && (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-500 mb-4">
                      Based on your credit score of <strong>{result.creditScore}</strong>, here are your KSA loan options:
                    </p>
                    {result.loanMatches.map((loan, index) => {
                      const config = getLoanStatusConfig(loan.matchStatus);
                      return (
                        <div key={index} className={`border rounded-xl p-5 ${config.cardBorder}`}>
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-4">
                              <div
                                className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                                style={{ backgroundColor: loan.color }}
                              >
                                {loan.logoInitials}
                              </div>
                              <div>
                                <h3 className="font-bold text-gray-800">{loan.bankName}</h3>
                                <p className="text-sm text-gray-500">{loan.productName}</p>
                                <p className="text-xs text-indigo-600 mt-1">{loan.highlight}</p>
                              </div>
                            </div>
                            <div className="text-right flex flex-col items-end gap-2">
                              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.badge}`}>
                                {config.label}
                              </span>
                              <span className="text-xs text-gray-400">{loan.matchPercentage}% match</span>
                            </div>
                          </div>

                          {/* Loan Details */}
                          <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-gray-100">
                            <div>
                              <p className="text-xs text-gray-400">Max Amount</p>
                              <p className="text-sm font-semibold text-gray-700">{loan.maxLoanAmount}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-400">Interest Rate</p>
                              <p className="text-sm font-semibold text-gray-700">{loan.interestRate}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-400">Processing Time</p>
                              <p className="text-sm font-semibold text-gray-700">{loan.processingTime}</p>
                            </div>
                          </div>

                          {/* Gaps — ALMOST */}
                          {loan.matchStatus === 'ALMOST' && loan.gaps.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-yellow-100">
                              <p className="text-xs font-semibold text-yellow-700 mb-2">To qualify, you need:</p>
                              <div className="space-y-1">
                                {loan.gaps.map((gap, i) => (
                                  <p key={i} className="text-xs text-yellow-600 flex items-center gap-1">
                                    <span>→</span> {gap}
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Gaps — NOT ELIGIBLE */}
                          {loan.matchStatus === 'NOT_ELIGIBLE' && loan.gaps.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-gray-100">
                              <p className="text-xs font-semibold text-gray-500 mb-2">Requirements not met:</p>
                              <div className="space-y-1">
                                {loan.gaps.map((gap, i) => (
                                  <p key={i} className="text-xs text-gray-400 flex items-center gap-1">
                                    <span>→</span> {gap}
                                  </p>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Qualified CTA */}
                          {loan.matchStatus === 'QUALIFIED' && (
                            <div className="mt-3 pt-3 border-t border-green-100">
                              <p className="text-xs text-green-600 font-medium">
                                ✅ You meet all requirements — you can apply for this loan today!
                              </p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* AI Explanation Tab */}
                {activeTab === 'explanation' && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                        <span className="text-indigo-600 text-xs font-bold">AI</span>
                      </div>
                      <span className="text-sm text-gray-500">Generated by Groq AI (Llama 3.3)</span>
                    </div>
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {result.aiExplanation}
                    </div>
                  </div>
                )}

                {/* Recommendations Tab */}
                {activeTab === 'recommendations' && (
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                        <span className="text-indigo-600 text-xs font-bold">AI</span>
                      </div>
                      <span className="text-sm text-gray-500">Personalized for your business</span>
                    </div>
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {result.aiRecommendations}
                    </div>
                  </div>
                )}

              </div>
            </div>

            {/* Submit Another */}
            <button
              onClick={() => setResult(null)}
              className="w-full py-3 border-2 border-indigo-200 text-indigo-600 rounded-xl font-semibold hover:bg-indigo-50 transition"
            >
              Submit Another Application
            </button>

          </div>
        )}

      </div>

      {/* AI Chat Assistant — only renders when result exists */}
      {result && <ChatAssistant business={result} />}

    </div>
  );
}