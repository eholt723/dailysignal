import { useState } from "react";

export default function Subscribe() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (res.ok) {
        setStatus("success");
        setEmail("");
      } else {
        const data = await res.json();
        setStatus(data.detail || "Something went wrong.");
      }
    } catch {
      setStatus("Network error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8 space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Subscribe</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Get AI-synthesized tech briefings delivered twice daily — morning and
          afternoon.
        </p>
      </div>

      {status === "success" ? (
        <div className="rounded-xl border border-green-300 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-5 text-green-700 dark:text-green-400 text-sm">
          You're subscribed. Check your inbox soon.
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="flex-1 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-cyan-600"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg transition-colors"
          >
            {loading ? "..." : "Subscribe"}
          </button>
        </form>
      )}

      {status && status !== "success" && (
        <p className="text-red-500 dark:text-red-400 text-sm">{status}</p>
      )}
    </div>
  );
}
