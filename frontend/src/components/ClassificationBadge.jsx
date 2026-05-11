const COLORS = {
  new_client: 'bg-green-100 text-green-800',
  support_request: 'bg-blue-100 text-blue-800',
  complaint: 'bg-red-100 text-red-800',
  general_question: 'bg-gray-100 text-gray-800',
};

const LABELS = {
  new_client: 'New Client',
  support_request: 'Support',
  complaint: 'Complaint',
  general_question: 'General',
};

export default function ClassificationBadge({ type }) {
  const colorClass = COLORS[type] || 'bg-gray-100 text-gray-800';
  const label = LABELS[type] || type;
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${colorClass}`}>
      {label}
    </span>
  );
}
