import { Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import History from "./pages/History";
import Admin from "./pages/Admin";
import Subscribe from "./pages/Subscribe";
import Unsubscribe from "./pages/Unsubscribe";
import About from "./pages/About";

const navLinks = [
  { to: "/", label: "Briefings", end: true },
  { to: "/history", label: "History" },
  { to: "/admin", label: "Admin" },
  { to: "/about", label: "About" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 px-4 py-3">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <span className="text-cyan-400 font-semibold tracking-tight text-lg">
            DailySignal
          </span>
          <nav className="flex items-center gap-6 text-sm">
            {navLinks.map(({ to, label, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  isActive
                    ? "text-cyan-400 font-medium"
                    : "text-gray-400 hover:text-gray-200 transition-colors"
                }
              >
                {label}
              </NavLink>
            ))}
            <NavLink
              to="/subscribe"
              className="bg-cyan-600 hover:bg-cyan-500 text-white text-sm px-3 py-1.5 rounded-lg transition-colors"
            >
              Subscribe
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<History />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/subscribe" element={<Subscribe />} />
          <Route path="/unsubscribe" element={<Unsubscribe />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <footer className="border-t border-gray-800 text-center text-xs text-gray-600 py-4 mt-12">
        DailySignal — AI news, twice daily
      </footer>
    </div>
  );
}
