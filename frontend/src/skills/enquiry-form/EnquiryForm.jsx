export default function EnquiryForm({ value, onChange, onSubmit, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) onSubmit(value);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste client enquiry here..."
        className="w-full h-[70vh] rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Analysing...' : 'Analyse Enquiry'}
      </button>
    </form>
  );
}
