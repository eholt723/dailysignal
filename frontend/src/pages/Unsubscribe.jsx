import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export default function Unsubscribe() {
  const [params] = useSearchParams();
  const token = params.get("token");
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    if (!token) {
      setStatus("invalid");
      return;
    }
    fetch(`/api/unsubscribe?token=${token}`, { method: "POST" })
      .then((r) => {
        if (r.ok) setStatus("success");
        else setStatus("invalid");
      })
      .catch(() => setStatus("error"));
  }, [token]);

  const messages = {
    loading: { text: "Processing...", color: "text-gray-400" },
    success: {
      text: "You've been unsubscribed. You won't receive any more briefings.",
      color: "text-green-400",
    },
    invalid: {
      text: "This unsubscribe link is invalid or has already been used.",
      color: "text-red-400",
    },
    error: { text: "Something went wrong. Please try again.", color: "text-red-400" },
  };

  const { text, color } = messages[status];

  return (
    <div className="max-w-md mx-auto mt-16 text-center space-y-3">
      <h1 className="text-xl font-semibold">Unsubscribe</h1>
      <p className={`text-sm ${color}`}>{text}</p>
    </div>
  );
}
