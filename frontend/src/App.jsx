import { useState } from 'react';
import EnquiryForm from './skills/enquiry-form/EnquiryForm';
import ResultCard from './skills/result-card/ResultCard';
import LoadingSpinner from './skills/shared/LoadingSpinner';
import ErrorBanner from './skills/shared/ErrorBanner';
import { classify } from './api';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleAnalyse(text) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await classify(text);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold text-gray-800">AI Enquiry Handler</h1>
          <p className="text-sm text-gray-500">Strata Management Consultants</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1">
            <EnquiryForm onSubmit={handleAnalyse} loading={loading} />
          </div>
          <div className="flex-1">
            {loading && <LoadingSpinner />}
            {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
            {result && !loading && <ResultCard result={result} />}
          </div>
        </div>
      </main>
    </div>
  );
}
