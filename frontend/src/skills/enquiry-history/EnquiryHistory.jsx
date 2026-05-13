import { useState } from 'react';
import ClassificationBadge from '../result-card/ClassificationBadge';

const PAGE_SIZE = 5;

export default function EnquiryHistory({ history, onSelect, onClear }) {
  const [page, setPage] = useState(1);

  const totalPages = Math.ceil(history.length / PAGE_SIZE);
  const visible = history.slice(0, page * PAGE_SIZE);
  const hasMore = visible.length < history.length;

  if (history.length === 0) return null;

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-800">History</h2>
        <button
          onClick={onClear}
          className="text-xs text-gray-400 hover:text-red-500 transition-colors"
        >
          Clear all
        </button>
      </div>
      <ul className="space-y-2">
        {visible.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => onSelect(item)}
              className="w-full text-left p-3 rounded-lg border border-gray-200 bg-white hover:bg-blue-50 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm text-gray-700 line-clamp-2 leading-snug flex-1 min-w-0">
                  {item.text}
                </p>
                {item.result?.classification?.type && (
                  <div className="shrink-0">
                    <ClassificationBadge type={item.result.classification.type} />
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {new Date(item.timestamp).toLocaleString()}
              </p>
            </button>
          </li>
        ))}
      </ul>
      {hasMore && (
        <button
          onClick={() => setPage((p) => p + 1)}
          className="mt-2 w-full text-sm text-blue-600 hover:text-blue-800 py-2 border border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors"
        >
          Show more ({history.length - visible.length} remaining)
        </button>
      )}
    </div>
  );
}
