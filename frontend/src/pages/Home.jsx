import { useEffect, useState } from "react";

function BriefingCard({ briefing }) {
  const label = briefing.period === "morning" ? "Morning" : "Afternoon";
  const date = new Date(briefing.run_at).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-cyan-400 uppercase tracking-wider">
          {label} Briefing
        </span>
        <span className="text-xs text-gray-500">{date}</span>
      </div>
      <div className="prose prose-invert prose-sm max-w-none text-gray-300 whitespace-pre-wrap leading-relaxed">
        {briefing.content}
      </div>
      <div className="pt-2 border-t border-gray-800 flex gap-4 flex-wrap text-xs text-gray-500">
        {Object.entries(briefing.source_counts).map(([source, count]) => (
          <span key={source}>
            {source}: {count}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function Home() {
  const [briefings, setBriefings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/briefings/latest")
      .then((r) => r.json())
      .then(setBriefings)
      .catch(() => setError("Failed to load briefings"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;
  if (error) return <p className="text-red-400 text-sm">{error}</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Latest Briefings</h1>
      {briefings.length === 0 ? (
        <p className="text-gray-500 text-sm">No briefings yet.</p>
      ) : (
        briefings.map((b) => <BriefingCard key={b.id} briefing={b} />)
      )}
    </div>
  );
}
