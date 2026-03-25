import { useEffect, useState } from "react";

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/admin/stats").then((r) => r.json()),
      fetch("/api/admin/deliveries").then((r) => r.json()),
    ])
      .then(([s, d]) => {
        setStats(s);
        setDeliveries(d);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Admin</h1>

      {stats && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "Total Subscribers", value: stats.total },
            { label: "Active", value: stats.active },
            { label: "Unsubscribed", value: stats.inactive },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 text-center"
            >
              <div className="text-2xl font-semibold text-cyan-600 dark:text-cyan-400">{value}</div>
              <div className="text-xs text-gray-500 mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-3">Recent Deliveries</h2>
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
          {deliveries.length === 0 ? (
            <p className="text-gray-500 text-sm p-6">No deliveries yet.</p>
          ) : (
            deliveries.map((d, i) => (
              <div key={i} className="flex items-center justify-between px-5 py-3 text-sm">
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      d.status === "sent"
                        ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400"
                        : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400"
                    }`}
                  >
                    {d.status}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">{d.email}</span>
                </div>
                <span className="text-gray-500 text-xs">
                  {new Date(d.attempted_at).toLocaleString()}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
