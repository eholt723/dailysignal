import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from "recharts";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function maskEmail(email) {
  if (!email) return "";
  const at = email.indexOf("@");
  if (at < 0) return email;
  const local = email.slice(0, at);
  const domain = email.slice(at + 1);
  const ext = domain.includes(".") ? domain.split(".").pop() : domain;
  return `${local.slice(0, 2)}***@***.${ext}`;
}

function fmtDay(dayStr) {
  if (!dayStr) return "";
  const d = new Date(dayStr + "T00:00:00Z");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
}

function fmtTs(ts) {
  const d = new Date(ts);
  return d.toLocaleDateString("en-US", {
    month: "short", day: "numeric", timeZone: "UTC",
  }) + " · " + d.toLocaleTimeString("en-US", {
    hour: "2-digit", minute: "2-digit", timeZone: "UTC", hour12: false,
  }) + " UTC";
}

// ---------------------------------------------------------------------------
// Chart theme helpers
// ---------------------------------------------------------------------------

const CHART_COLORS = ["#06b6d4", "#8b5cf6", "#f59e0b", "#10b981", "#f43f5e", "#3b82f6"];

const axisStyle = { fill: "#9ca3af", fontSize: 11 };
const gridStyle = { stroke: "#1f2937" };

const darkTooltip = {
  contentStyle: {
    background: "#111827",
    border: "1px solid #374151",
    borderRadius: "8px",
    fontSize: "12px",
    color: "#f3f4f6",
  },
  itemStyle: { color: "#f3f4f6" },
  labelStyle: { color: "#9ca3af" },
};

// ---------------------------------------------------------------------------
// Stat card
// ---------------------------------------------------------------------------

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 text-center">
      <div className="text-2xl font-semibold text-cyan-600 dark:text-cyan-400">{value ?? "—"}</div>
      <div className="text-xs text-gray-500 mt-1 leading-tight">{label}</div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section heading
// ---------------------------------------------------------------------------

function SectionHead({ children }) {
  return <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{children}</h2>;
}

// ---------------------------------------------------------------------------
// Briefing card (expandable)
// ---------------------------------------------------------------------------

function BriefingRow({ briefing }) {
  const [expanded, setExpanded] = useState(false);
  const label = briefing.period === "morning" ? "Morning Brief" : "Afternoon Brief";
  const totalItems = Object.values(briefing.source_counts || {}).reduce((a, b) => a + b, 0);

  return (
    <div className="border-b border-gray-200 dark:border-gray-800 last:border-0">
      <div className="flex items-center justify-between px-5 py-3">
        <div className="flex items-center gap-3 min-w-0">
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${
              briefing.period === "morning"
                ? "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400"
                : "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-400"
            }`}
          >
            {label}
          </span>
          <span className="text-sm text-gray-700 dark:text-gray-300 truncate">{fmtTs(briefing.run_at)}</span>
          <span className="text-xs text-gray-500 shrink-0">{totalItems} items</span>
        </div>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="text-xs text-cyan-600 dark:text-cyan-400 hover:underline shrink-0 ml-3"
        >
          {expanded ? "Collapse" : "View Brief"}
        </button>
      </div>
      {expanded && (
        <div className="px-5 pb-5">
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-950 p-4 text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-2">
            <ReactMarkdown
              components={{
                h2: ({ children }) => (
                  <h2 className="text-base font-semibold text-gray-800 dark:text-gray-200 mt-4 mb-1">{children}</h2>
                ),
                p: ({ children }) => <p className="mb-2">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-5 space-y-1">{children}</ul>,
                li: ({ children }) => <li>{children}</li>,
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer"
                    className="text-cyan-600 dark:text-cyan-400 hover:underline">{children}</a>
                ),
              }}
            >
              {briefing.content}
            </ReactMarkdown>
          </div>
          <div className="mt-2 flex gap-4 flex-wrap text-xs text-gray-500">
            {Object.entries(briefing.source_counts || {}).map(([source, count]) => (
              <span key={source}>{source}: {count}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard
// ---------------------------------------------------------------------------

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [charts, setCharts] = useState(null);
  const [briefings, setBriefings] = useState([]);
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/admin/stats").then((r) => r.json()),
      fetch("/api/admin/charts").then((r) => r.json()),
      fetch("/api/briefings/recent").then((r) => r.json()),
      fetch("/api/admin/deliveries").then((r) => r.json()),
    ])
      .then(([s, c, b, d]) => {
        setStats(s);
        setCharts(c);
        setBriefings(b);
        setDeliveries(d);
      })
      .catch(() => setError("Failed to load dashboard data"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;
  if (error) return <p className="text-red-500 text-sm">{error}</p>;

  return (
    <div className="space-y-8">

      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <StatCard label="Total Subscribers" value={stats?.total} />
        <StatCard label="Active Subscribers" value={stats?.active} />
        <StatCard label="Unsubscribed" value={stats?.inactive} />
        <StatCard label="Briefings Sent" value={stats?.total_briefings} />
        <StatCard
          label="Delivery Success"
          value={stats?.delivery_success_rate != null ? `${stats.delivery_success_rate}%` : "—"}
        />
      </div>

      {/* Charts */}
      {charts && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

          {/* Briefings per day */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 space-y-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Briefings per day</p>
            {charts.briefings_per_day.length === 0 ? (
              <p className="text-xs text-gray-500">No data</p>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={charts.briefings_per_day} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" {...gridStyle} />
                  <XAxis dataKey="day" tickFormatter={fmtDay} tick={axisStyle} />
                  <YAxis tick={axisStyle} allowDecimals={false} />
                  <Tooltip {...darkTooltip} labelFormatter={fmtDay} />
                  <Bar dataKey="count" fill="#0891b2" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Source breakdown donut */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 space-y-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Source breakdown</p>
            {charts.source_breakdown.length === 0 ? (
              <p className="text-xs text-gray-500">No data</p>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie
                    data={charts.source_breakdown}
                    dataKey="count"
                    nameKey="source"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={65}
                    paddingAngle={2}
                  >
                    {charts.source_breakdown.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip {...darkTooltip} />
                </PieChart>
              </ResponsiveContainer>
            )}
            <div className="flex flex-wrap gap-x-3 gap-y-1">
              {charts.source_breakdown.map((s, i) => (
                <span key={s.source} className="flex items-center gap-1 text-xs text-gray-500">
                  <span
                    className="inline-block w-2 h-2 rounded-full"
                    style={{ background: CHART_COLORS[i % CHART_COLORS.length] }}
                  />
                  {s.source}
                </span>
              ))}
            </div>
          </div>

          {/* Delivery success vs failed */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 space-y-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Deliveries per day</p>
            {charts.delivery_by_day.length === 0 ? (
              <p className="text-xs text-gray-500">No data</p>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={charts.delivery_by_day} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" {...gridStyle} />
                  <XAxis dataKey="day" tickFormatter={fmtDay} tick={axisStyle} />
                  <YAxis tick={axisStyle} allowDecimals={false} />
                  <Tooltip {...darkTooltip} labelFormatter={fmtDay} />
                  <Bar dataKey="sent" fill="#10b981" radius={[3, 3, 0, 0]} stackId="a" />
                  <Bar dataKey="failed" fill="#ef4444" radius={[3, 3, 0, 0]} stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            )}
            <div className="flex gap-4 text-xs text-gray-500">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />Sent</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500 inline-block" />Failed</span>
            </div>
          </div>

          {/* Subscriber growth */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 space-y-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Subscriber growth</p>
            {charts.subscriber_growth.length === 0 ? (
              <p className="text-xs text-gray-500">No data</p>
            ) : (
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={charts.subscriber_growth} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" {...gridStyle} />
                  <XAxis dataKey="day" tickFormatter={fmtDay} tick={axisStyle} />
                  <YAxis tick={axisStyle} allowDecimals={false} />
                  <Tooltip {...darkTooltip} labelFormatter={fmtDay} />
                  <Line
                    type="monotone"
                    dataKey="total"
                    stroke="#0891b2"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

        </div>
      )}

      {/* Recent Briefings */}
      <div className="space-y-3">
        <SectionHead>Recent Briefings</SectionHead>
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
          {briefings.length === 0 ? (
            <p className="text-gray-500 text-sm p-6">No briefings yet.</p>
          ) : (
            briefings.map((b) => <BriefingRow key={b.id} briefing={b} />)
          )}
        </div>
      </div>

      {/* Recent Deliveries */}
      <div className="space-y-3">
        <SectionHead>Recent Deliveries</SectionHead>
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
                  <span className="text-gray-600 dark:text-gray-400 font-mono text-xs">{maskEmail(d.email)}</span>
                </div>
                <span className="text-gray-500 text-xs">{fmtTs(d.attempted_at)}</span>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
