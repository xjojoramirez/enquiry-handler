export default function ConfidenceMeter({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct > 80 ? 'bg-green-500' : pct > 50 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm text-gray-600 w-10 text-right">{pct}%</span>
    </div>
  );
}
