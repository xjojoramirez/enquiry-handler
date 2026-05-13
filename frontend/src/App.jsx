import { useState } from 'react';
import EnquiryForm from './skills/enquiry-form/EnquiryForm';
import EnquiryHistory from './skills/enquiry-history/EnquiryHistory';
import ResultCard from './skills/result-card/ResultCard';
import LoadingSpinner from './skills/shared/LoadingSpinner';
import ErrorBanner from './skills/shared/ErrorBanner';
import { classify } from './api';

const HISTORY_KEY = 'enquiry-history';
const MAX_HISTORY = 50;

function loadHistory() {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

export default function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState(loadHistory);

  async function handleAnalyse(enquiryText) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await classify(enquiryText);
      setResult(data);
      const entry = {
        id: Date.now(),
        text: enquiryText,
        result: data,
        timestamp: new Date().toISOString(),
      };
      const updated = [entry, ...history].slice(0, MAX_HISTORY);
      setHistory(updated);
      saveHistory(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleHistorySelect(item) {
    setText(item.text);
    setResult(item.result);
    setError(null);
  }

  function handleClearHistory() {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
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
            <EnquiryForm
              value={text}
              onChange={setText}
              onSubmit={handleAnalyse}
              loading={loading}
            />
            <EnquiryHistory
              history={history}
              onSelect={handleHistorySelect}
              onClear={handleClearHistory}
            />
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
