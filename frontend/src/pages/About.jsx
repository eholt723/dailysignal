import { Link } from "react-router-dom";

const PIPELINE_STEPS = [
  {
    num: "01",
    title: "Fetch",
    desc: "Every 8 hours, a GitHub Actions job pulls from HackerNews, Product Hunt, and five RSS feeds — no servers to keep alive.",
  },
  {
    num: "02",
    title: "Deduplicate",
    desc: "Each item is hashed and checked against previously stored hashes in PostgreSQL. Only genuinely new items make it through.",
  },
  {
    num: "03",
    title: "Synthesize",
    desc: "New items are sent to a Groq-hosted LLM which writes a structured briefing: top stories, product highlights, and community picks.",
  },
  {
    num: "04",
    title: "Store",
    desc: "The briefing and all raw items land in Neon PostgreSQL — available instantly to the frontend API.",
  },
  {
    num: "05",
    title: "Email",
    desc: "The briefing is sent to every active subscriber via Gmail SMTP. Each email has a unique unsubscribe link.",
  },
  {
    num: "06",
    title: "Serve",
    desc: "The React frontend on Hugging Face Spaces shows the latest briefings, run history, and subscriber stats — always up to date.",
  },
];

const ACHIEVEMENTS = [
  "Fully automated pipeline — zero manual steps from fetch to inbox",
  "Cross-source deduplication using SHA-256 content hashes",
  "LLM-synthesized briefings via Groq with structured section formatting",
  "Per-subscriber unsubscribe tokens and automatic deactivation after 3 failures",
  "GitHub Actions cron scheduling — no always-on server required",
  "PostgreSQL on Neon with delivery audit log per subscriber per run",
  "React + Vite frontend deployed as Docker on Hugging Face Spaces",
  "Admin dashboard: subscriber counts and last 10 delivery statuses",
];

const STACK = [
  { name: "Python", role: "Pipeline orchestration" },
  { name: "Groq", role: "LLM inference (briefing generation)" },
  { name: "GitHub Actions", role: "Cron scheduling and CI" },
  { name: "PostgreSQL / Neon", role: "Briefing storage and delivery logs" },
  { name: "Gmail SMTP", role: "Email delivery" },
  { name: "React + Vite", role: "Frontend" },
  { name: "Tailwind CSS", role: "Styling" },
  { name: "Hugging Face Spaces", role: "Frontend hosting (Docker)" },
];

const USE_CASES = [
  {
    title: "Sales Performance Digest",
    desc: "Every Monday, sales managers receive an AI-written summary of last week's pipeline — deals closed, deals stalled, top performers, and flagged risks — pulled automatically from CRM data, no manual report building required.",
  },
  {
    title: "E-Commerce Inventory Alerts",
    desc: "Every night the system checks stock levels against sales velocity, identifies items trending toward stockout or overstock, and delivers a prioritized reorder recommendation to the operations team before the warehouse opens.",
  },
  {
    title: "Financial Anomaly Report",
    desc: "Daily pull of transaction data, AI analysis for unusual patterns — unexpected charges, budget overruns, duplicate payments — delivered to finance leads before the business day starts.",
  },
  {
    title: "Marketing Campaign Digest",
    desc: "Weekly summary of campaign performance across channels with an AI-written narrative explaining what worked, what didn't, and what to adjust.",
  },
  {
    title: "Infrastructure Health Summary",
    desc: "Nightly report of system uptime, error rates, and performance metrics across services, with an AI-written triage note flagging anything that needs attention before the engineering team starts work.",
  },
  {
    title: "Competitor Monitoring Brief",
    desc: "Weekly scrape of competitor pricing pages, product updates, and job postings, synthesized into a structured brief delivered to product and strategy teams automatically.",
  },
];

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 space-y-16">
      {/* Hero */}
      <section className="space-y-4">
        <h1 className="text-3xl font-bold text-gray-100">About DailySignal</h1>
        <p className="text-base text-gray-400 leading-relaxed">
          DailySignal automatically tracks what's happening in tech and AI — so you don't have to
          tab through five sites every morning. Twice a day, it fetches from HackerNews, Product
          Hunt, and top tech blogs, filters out what you've already seen, and sends a clean,
          AI-written briefing straight to your inbox.
        </p>
        <p className="text-base text-gray-400 leading-relaxed">
          The whole pipeline runs on GitHub Actions — no servers to keep alive, no cron jobs to
          babysit.
        </p>
      </section>

      {/* How It Works */}
      <section className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-100">How It Works</h2>
        <div className="space-y-0">
          {PIPELINE_STEPS.map((step, i) => (
            <div key={step.num} className="flex gap-5">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-cyan-900/50 border border-cyan-700 flex items-center justify-center text-xs font-mono text-cyan-400 shrink-0">
                  {step.num}
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div className="w-px flex-1 bg-gray-800 my-1" />
                )}
              </div>
              <div className="pb-8">
                <div className="text-sm font-semibold text-gray-100 mb-1">{step.title}</div>
                <div className="text-sm text-gray-400 leading-relaxed">{step.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* What Was Built */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-100">What Was Built</h2>
        <ul className="space-y-2">
          {ACHIEVEMENTS.map((a) => (
            <li key={a} className="flex items-start gap-2 text-sm text-gray-400">
              <span className="text-cyan-500 mt-0.5 shrink-0">✓</span>
              {a}
            </li>
          ))}
        </ul>
      </section>

      {/* Tech Stack */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-100">Tech Stack</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {STACK.map((s) => (
            <div
              key={s.name}
              className="rounded-xl border border-gray-800 bg-gray-900 p-3"
            >
              <div className="text-sm font-medium text-gray-100">{s.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">{s.role}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Where This Gets Used */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-100">Where This Gets Used</h2>
        <p className="text-sm text-gray-400">
          DailySignal demonstrates a pattern — scheduled data fetch, LLM synthesis, automated
          delivery — that applies across industries. A few examples:
        </p>
        <div className="space-y-3">
          {USE_CASES.map((uc) => (
            <div
              key={uc.title}
              className="rounded-xl border border-gray-800 bg-gray-900 p-4 space-y-1"
            >
              <div className="text-sm font-semibold text-gray-100">{uc.title}</div>
              <div className="text-sm text-gray-400 leading-relaxed">{uc.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Links */}
      <section className="flex gap-3">
        <Link
          to="/"
          className="bg-cyan-600 hover:bg-cyan-500 text-white text-sm px-5 py-2.5 rounded-lg transition-colors"
        >
          Try the App
        </Link>
        <a
          href="https://github.com/eholt723/dailysignal"
          target="_blank"
          rel="noreferrer"
          className="border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-gray-100 text-sm px-5 py-2.5 rounded-lg transition-colors"
        >
          View on GitHub
        </a>
      </section>
    </div>
  );
}
