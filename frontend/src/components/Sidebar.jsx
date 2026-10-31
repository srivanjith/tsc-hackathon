import React from "react";
import {
  LayoutDashboard,
  Brain,
  Layers,
  Route,
  History,
  ShieldAlert,
  Radio,
  CheckCircle2,
  Globe2,
} from "lucide-react";

export default function Sidebar({ activeTab, onTabChange, pendingApprovals = 0 }) {
  const navItems = [
    {
      id: "dashboard",
      label: "National Command Grid",
      icon: LayoutDashboard,
      badge: "Live",
      badgeColor: "bg-emerald-800 text-emerald-200",
    },
    {
      id: "intelligence",
      label: "Multi-Hazard & NLP",
      icon: Brain,
      badge: "RF + Groq",
      badgeColor: "bg-purple-800 text-purple-200",
    },
    {
      id: "operations",
      label: "NDRF & Strategic Fleet",
      icon: Layers,
      badge: null,
    },
    {
      id: "replanning",
      label: "RippleGuard Replanning",
      icon: Route,
      badge: pendingApprovals > 0 ? `${pendingApprovals} Pending` : "P0 Core",
      badgeColor: pendingApprovals > 0 ? "bg-amber-500 text-white" : "bg-blue-800 text-blue-200",
    },
    {
      id: "decisions",
      label: "Commander Audit Logs",
      icon: History,
      badge: null,
    },
  ];

  return (
    <aside className="w-64 bg-[#102B46] text-white flex flex-col justify-between shrink-0 shadow-xl z-20 min-h-screen">
      <div>
        {/* Logo and Brand */}
        <div className="p-5 border-b border-slate-700/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#1677D2] flex items-center justify-center shadow-lg shadow-blue-500/30">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg tracking-tight text-white font-mono">
                  ResQAI<span className="text-rose-400">/RELIEF-X</span>
                </span>
              </div>
              <p className="text-[10px] text-slate-300 leading-tight mt-0.5">
                Pan-India Multi-Hazard Coordinator
              </p>
            </div>
          </div>

          <div className="mt-3 px-2.5 py-1.5 rounded-lg bg-slate-800/70 border border-slate-700 flex items-center justify-between text-[11px]">
            <span className="text-slate-300 flex items-center gap-1.5">
              <Globe2 className="w-3.5 h-3.5 text-blue-400" />
              Coverage:
            </span>
            <span className="font-semibold text-emerald-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              All-India Grid (7 Hubs)
            </span>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-3 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#1677D2] text-white shadow-md shadow-blue-900/40 font-semibold"
                    : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                      item.badgeColor || "bg-slate-700 text-slate-200"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer system details */}
      <div className="p-4 border-t border-slate-700/60 text-[11px] text-slate-400 space-y-2">
        <div className="flex items-center justify-between">
          <span>Routing Engine:</span>
          <span className="text-cyan-300 font-mono">NetworkX / Dijkstra</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Risk Model:</span>
          <span className="text-emerald-300 font-mono">Random Forest</span>
        </div>
        <div className="flex items-center justify-between">
          <span>NLP Verifier:</span>
          <span className="text-purple-300 font-mono">TF-IDF + Groq LLaMA</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Human-in-the-Loop:</span>
          <span className="text-rose-300 font-mono">Enforced</span>
        </div>
      </div>
    </aside>
  );
}
