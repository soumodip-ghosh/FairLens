import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './index.css';

function App() {
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [target, setTarget] = useState('');
  const [sensitive, setSensitive] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
    
    const formData = new FormData();
    formData.append('file', uploadedFile);

    const res = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    setColumns(data.columns);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target', target);
    formData.append('sensitive', sensitive);

    const res = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    setResults(data);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            🔍 FairLens <span className="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded-full">Gemini Edition</span>
          </h1>
          <p className="text-gray-500 mt-2">Detect and explain bias in your machine learning datasets.</p>
        </div>

        {/* Upload & Config */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <input 
            type="file" 
            accept=".csv" 
            onChange={handleFileUpload}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />

          {columns.length > 0 && (
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Target Column (Prediction)</label>
                <select onChange={(e) => setTarget(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border">
                  <option value="">Select Target...</option>
                  {columns.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Sensitive Attribute (Bias Check)</label>
                <select onChange={(e) => setSensitive(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border">
                  <option value="">Select Sensitive Col...</option>
                  {columns.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              
              <button 
                onClick={handleAnalyze}
                disabled={!target || !sensitive || loading}
                className="col-span-2 mt-4 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Analyzing with Gemini...' : 'Run Bias Detection'}
              </button>
            </div>
          )}
        </div>

        {/* Results Dashboard */}
        {results && !results.error && (
          <div className="space-y-6">
            
            {/* Alert Banner */}
            <div className={`p-4 rounded-md font-bold flex items-center justify-between ${results.is_biased ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
              <span>{results.is_biased ? '⚠️ Potential Bias Detected' : '✅ Model Looks Fair'}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Metrics Box */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold mb-4">Fairness Metrics</h3>
                <ul className="space-y-3">
                  {Object.entries(results.metrics).map(([key, value]) => (
                    <li key={key} className="flex justify-between text-sm">
                      <span className="text-gray-600">{key}:</span>
                      <span className="font-mono font-medium">{Number(value).toFixed(3)}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Gemini Explanation */}
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-xl shadow-sm border border-indigo-100">
                <h3 className="text-lg font-bold mb-4 text-indigo-900 flex items-center gap-2">✨ Gemini AI Explanation</h3>
                <div className="prose prose-sm text-gray-800">
                  <ReactMarkdown>{results.explanation}</ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {results?.error && (
          <div className="bg-red-100 text-red-800 p-4 rounded-md">Error: {results.error}</div>
        )}

      </div>
    </div>
  );
}

export default App;