import { useEffect, useState } from "react";

export default function History() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/briefings/history")
      .then((r) => r.json())
      .then(setRuns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Run History</h1>
      <div className="rounded-xl border border-gray-800 bg-gray-900 divide-y divide-gray-800">
        {runs.length === 0 ? (
          <p className="text-gray-500 text-sm p-6">No runs yet.</p>
        ) : (
          runs.map((run) => {
            const dt = new Date(run.run_at);
            const totalItems = Object.values(run.source_counts).reduce(
              (a, b) => a + b,
              0
            );
            return (
              <div key={run.id} className="flex items-center justify-between px-5 py-3 text-sm">
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      run.period === "morning"
                        ? "bg-amber-900/40 text-amber-400"
                        : "bg-indigo-900/40 text-indigo-400"
                    }`}
                  >
                    {run.period}
                  </span>
                  <span className="text-gray-300">
                    {dt.toLocaleDateString("en-US", {
                      weekday: "short",
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                  <span className="text-gray-500">
                    {dt.toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                <span className="text-gray-500 text-xs">{totalItems} items</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
