import { useState } from 'react';
import { createBusiness } from '../services/api';
import type { BusinessRequest, BusinessResponse } from '../services/api';

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
  const [activeTab, setActiveTab] = useState<'explanation' | 'recommendations'>('explanation');

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await createBusiness(form);
      setResult(res.data);
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

  const scorePercent = result ? (result.creditScore / 100) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-indigo-700">AltScore</h1>
          <p className="text-gray-500 mt-1">AI-Powered Alternative Credit Scoring for SMEs</p>
        </div>

        {/* Form */}
        {!result && (
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">Business Credit Application</h2>
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
              className="mt-6 w-full bg-indigo-600 text-white py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                  Analyzing with AI...
                </span>
              ) : 'Get AI Credit Score'}
            </button>
          </div>
        )}

        {/* Results Dashboard */}
        {result && (
          <div className="space-y-6">

            {/* Score Card */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">{result.businessName}</h2>
                  <p className="text-gray-500">{result.ownerName} · {result.businessType}</p>
                </div>
                <button
                  onClick={() => setResult(null)}
                  className="text-sm text-indigo-600 hover:underline"
                >
                  New Application
                </button>
              </div>

              <div className="mt-6 flex items-center gap-12">
                {/* Score Circle */}
                <div className="text-center">
                  <div className="relative w-36 h-36">
                    <svg viewBox="0 0 36 36" className="w-36 h-36 -rotate-90">
                      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3"/>
                      <circle
                        cx="18" cy="18" r="15.9" fill="none"
                        stroke={result.creditScore >= 80 ? '#16a34a' : result.creditScore >= 60 ? '#ca8a04' : result.creditScore >= 40 ? '#ea580c' : '#dc2626'}
                        strokeWidth="3"
                        strokeDasharray={`${scorePercent} 100`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className={`text-3xl font-bold ${getScoreColor(result.creditScore)}`}>
                        {result.creditScore}
                      </span>
                      <span className="text-xs text-gray-400">/ 100</span>
                    </div>
                  </div>
                  <p className={`mt-2 font-semibold ${getScoreColor(result.creditScore)}`}>
                    {getScoreLabel(result.creditScore)}
                  </p>
                </div>

                {/* Stats */}
                <div className="flex-1 grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-gray-800">SAR {result.monthlyRevenue.toLocaleString()}</p>
                    <p className="text-xs text-gray-500 mt-1">Monthly Revenue</p>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-gray-800">{result.yearsInOperation}y</p>
                    <p className="text-xs text-gray-500 mt-1">In Operation</p>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-gray-800">{result.numTransactions}</p>
                    <p className="text-xs text-gray-500 mt-1">Monthly Transactions</p>
                  </div>
                </div>

                {/* Risk Badge */}
                <div className="text-center">
                  <p className="text-sm text-gray-500 mb-2">Risk Level</p>
                  <span className={`px-5 py-2 rounded-full font-bold text-sm border ${getRiskColor(result.riskLevel).bg} ${getRiskColor(result.riskLevel).text} ${getRiskColor(result.riskLevel).border}`}>
                    {result.riskLevel}
                  </span>
                </div>
              </div>
            </div>

            {/* AI Analysis Card */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="flex border-b">
                <button
                  onClick={() => setActiveTab('explanation')}
                  className={`flex-1 py-4 font-semibold text-sm transition ${activeTab === 'explanation' ? 'bg-indigo-600 text-white' : 'text-gray-500 hover:bg-gray-50'}`}
                >
                  AI Score Explanation
                </button>
                <button
                  onClick={() => setActiveTab('recommendations')}
                  className={`flex-1 py-4 font-semibold text-sm transition ${activeTab === 'recommendations' ? 'bg-indigo-600 text-white' : 'text-gray-500 hover:bg-gray-50'}`}
                >
                  AI Recommendations
                </button>
              </div>

              <div className="p-8">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                    <span className="text-indigo-600 text-xs font-bold">AI</span>
                  </div>
                  <span className="text-sm text-gray-500">Generated by GROQ AI</span>
                </div>

                <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {activeTab === 'explanation'
                    ? result.aiExplanation
                    : result.aiRecommendations}
                </div>
              </div>
            </div>

            {/* Apply Again */}
            <button
              onClick={() => setResult(null)}
              className="w-full py-3 border-2 border-indigo-200 text-indigo-600 rounded-xl font-semibold hover:bg-indigo-50 transition"
            >
              Submit Another Application
            </button>

          </div>
        )}
      </div>
    </div>
  );
}