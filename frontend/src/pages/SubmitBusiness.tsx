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
      case 'LOW': return 'text-green-600 bg-green-100';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100';
      case 'HIGH': return 'text-orange-600 bg-orange-100';
      case 'VERY_HIGH': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-primary-700 mb-2">AltScore</h1>
        <p className="text-gray-500 mb-8">Alternative Credit Scoring for SMEs</p>

        <div className="bg-white rounded-2xl shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Business Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">Business Name</label>
              <input
                className="w-full border rounded-lg p-2 mt-1"
                value={form.businessName}
                onChange={e => setForm({ ...form, businessName: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">Owner Name</label>
              <input
                className="w-full border rounded-lg p-2 mt-1"
                value={form.ownerName}
                onChange={e => setForm({ ...form, ownerName: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">Business Type</label>
              <select
                className="w-full border rounded-lg p-2 mt-1"
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
              <label className="text-sm text-gray-600">Monthly Revenue (SAR)</label>
              <input
                type="number"
                className="w-full border rounded-lg p-2 mt-1"
                value={form.monthlyRevenue}
                onChange={e => setForm({ ...form, monthlyRevenue: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">Years in Operation</label>
              <input
                type="number"
                className="w-full border rounded-lg p-2 mt-1"
                value={form.yearsInOperation}
                onChange={e => setForm({ ...form, yearsInOperation: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">Monthly Transactions</label>
              <input
                type="number"
                className="w-full border rounded-lg p-2 mt-1"
                value={form.numTransactions}
                onChange={e => setForm({ ...form, numTransactions: Number(e.target.value) })}
              />
            </div>
          </div>

          {error && <p className="text-red-500 mt-4 text-sm">{error}</p>}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="mt-6 w-full bg-primary-600 text-white py-3 rounded-xl font-semibold hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Scoring...' : 'Get Credit Score'}
          </button>
        </div>

        {result && (
          <div className="bg-white rounded-2xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Credit Score Result</h2>
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-gray-500 text-sm">Credit Score</p>
                <p className="text-5xl font-bold text-primary-600">{result.creditScore}</p>
                <p className="text-gray-400 text-sm">out of 100</p>
              </div>
              <div>
                <p className="text-gray-500 text-sm mb-1">Risk Level</p>
                <span className={`px-4 py-2 rounded-full font-semibold text-sm ${getRiskColor(result.riskLevel)}`}>
                  {result.riskLevel}
                </span>
              </div>
            </div>
            <div className="border-t pt-4 space-y-1">
              <p className="text-sm text-gray-500">
                Business: <span className="font-medium text-gray-800">{result.businessName}</span>
              </p>
              <p className="text-sm text-gray-500">
                Owner: <span className="font-medium text-gray-800">{result.ownerName}</span>
              </p>
              <p className="text-sm text-gray-500">
                Type: <span className="font-medium text-gray-800">{result.businessType}</span>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}