import ClassificationBadge from './ClassificationBadge';
import ConfidenceMeter from './ConfidenceMeter';

export default function ResultCard({ result }) {
  if (!result) return null;
  const { classification, priority, summary, entities, recommended_team, suggested_response } = result;

  const priorityColor =
    priority === 'high' ? 'text-red-600' : priority === 'medium' ? 'text-yellow-600' : 'text-green-600';

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <ClassificationBadge type={classification?.type} />
        <span className={`font-semibold capitalize ${priorityColor}`}>{priority} Priority</span>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-1">Confidence</p>
        <ConfidenceMeter value={classification?.confidence} />
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-1">Summary</p>
        <p>{summary}</p>
      </div>

      {entities && Object.keys(entities).length > 0 && (
        <div>
          <p className="text-sm text-gray-500 mb-1">Entities</p>
          <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
            <tbody>
              {Object.entries(entities).filter(([, v]) => v !== null && v !== undefined && !(Array.isArray(v) && v.length === 0)).map(([key, value]) => (
                <tr key={key} className="border-b border-gray-200 last:border-0">
                  <td className="px-3 py-2 font-medium capitalize bg-gray-50 w-1/3">{key.replace(/_/g, ' ')}</td>
                  <td className="px-3 py-2">{Array.isArray(value) ? value.join(', ') : String(value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div>
        <p className="text-sm text-gray-500 mb-1">Recommended Team</p>
        <p className="font-medium">{recommended_team}</p>
      </div>

      <div>
        <p className="text-sm text-gray-500 mb-1">Suggested Response</p>
        <div className="bg-gray-50 border border-gray-200 rounded p-3 whitespace-pre-wrap text-sm">
          {suggested_response}
        </div>
      </div>
    </div>
  );
}
