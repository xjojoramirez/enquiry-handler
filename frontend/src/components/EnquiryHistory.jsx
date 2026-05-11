import { useState, useEffect } from 'react';
import { listEnquiries } from '../api';

export default function EnquiryHistory({ onSelect }) {
  const [enquiries, setEnquiries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listEnquiries()
      .then(setEnquiries)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-gray-400">Loading...</p>;
  if (enquiries.length === 0) return <p className="text-sm text-gray-400">No enquiries yet.</p>;

  return (
    <div className="space-y-2">
      <h3 className="font-semibold text-gray-700 mb-2">History</h3>
      {enquiries.map((e) => (
        <button
          key={e.id}
          onClick={() => onSelect(e)}
          className="w-full text-left p-2 rounded hover:bg-gray-100 text-sm truncate border border-gray-100"
        >
          <span className="font-medium capitalize text-xs text-gray-500">{e.classification?.type}</span>
          <p className="truncate">{e.summary}</p>
        </button>
      ))}
    </div>
  );
}
