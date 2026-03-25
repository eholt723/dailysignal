import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

function BriefingCard({ briefing }) {
  const label = briefing.period === "morning" ? "Morning" : "Afternoon";
  const d = new Date(briefing.run_at);
  const date = d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
  const time = d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    hour12: false,
  });

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">
          {label} Briefing
        </span>
        <span className="text-xs text-gray-500">{date} · {time} UTC</span>
      </div>
      <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-2">
        <ReactMarkdown
          components={{
            h2: ({ children }) => (
              <h2 className="text-base font-semibold text-gray-800 dark:text-gray-200 mt-4 mb-1">
                {children}
              </h2>
            ),
            p: ({ children }) => <p className="mb-2">{children}</p>,
            ul: ({ children }) => <ul className="list-disc pl-5 space-y-1">{children}</ul>,
            li: ({ children }) => <li>{children}</li>,
            a: ({ href, children }) => (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-600 dark:text-cyan-400 hover:underline"
              >
                {children}
              </a>
            ),
          }}
        >
          {briefing.content}
        </ReactMarkdown>
      </div>
      <div className="pt-2 border-t border-gray-200 dark:border-gray-800 flex gap-4 flex-wrap text-xs text-gray-500">
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
  if (error) return <p className="text-red-500 text-sm">{error}</p>;

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
