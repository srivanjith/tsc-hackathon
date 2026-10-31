import React from "react";
import {
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Send,
  Route,
  Activity,
  Radio,
} from "lucide-react";

export default function MetricsHeader({ kpi, onFilterSelect, currentFilter }) {
  if (!kpi) return null;

  const cards = [
    {
      id: "ALL",
      label: "Total Incidents",
      value: kpi.total_incidents,
      sub: "Active threat records",
      icon: AlertTriangle,
      color: "border-slate-700 bg-slate-900/80 text-white",
      iconColor: "text-slate-400 bg-slate-800",
      filterKey: "ALL",
    },
    {
      id: "CRITICAL",
      label: "Critical Threats",
      value: kpi.critical_incidents,
      sub: "Priority Score ≥ 75",
      icon: ShieldAlert,
      color: "border-rose-900/60 bg-rose-950/30 text-rose-300",
      iconColor: "text-rose-400 bg-rose-900/50",
      filterKey: "CRITICAL",
      badge: "Immediate Action",
    },
    {
      id: "FALSE_ALARMS",
      label: "False Alarms Filtered",
      value: kpi.false_alarms_filtered,
      sub: "Trust < 50% held in review",
      icon: ShieldCheck,
      color: "border-emerald-900/60 bg-emerald-950/30 text-emerald-300",
      iconColor: "text-emerald-400 bg-emerald-900/50",
      filterKey: "UNDER_REVIEW",
      badge: "Saved Diversions",
    },
    {
      id: "DISPATCHED",
      label: "Active Deployments",
      value: kpi.active_dispatches,
      sub: "Rescue teams on route",
      icon: Send,
      color: "border-blue-900/60 bg-blue-950/30 text-blue-300",
      iconColor: "text-blue-400 bg-blue-900/50",
      filterKey: "DISPATCHED",
    },
    {
      id: "REROUTED",
      label: "Dynamic Detours",
      value: kpi.rerouted_units,
      sub: "Auto-replanned routes",
      icon: Route,
      color: "border-amber-900/60 bg-amber-950/30 text-amber-300",
      iconColor: "text-amber-400 bg-amber-900/50",
      badge: "Live Re-route",
    },
    {
      id: "SENSORS",
      label: "Avg Trust Score",
      value: `${Math.round(kpi.average_credibility * 100)}%`,
      sub: `${kpi.active_sensors} active IoT sensors`,
      icon: Activity,
      color: "border-purple-900/60 bg-purple-950/30 text-purple-300",
      iconColor: "text-purple-400 bg-purple-900/50",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      {cards.map((card) => {
        const Icon = card.icon;
        const isSelected = currentFilter === card.filterKey;

        return (
          <div
            key={card.id}
            onClick={() => card.filterKey && onFilterSelect && onFilterSelect(card.filterKey)}
            className={`p-3.5 rounded-xl border backdrop-blur-sm transition-all duration-200 ${card.color} ${
              card.filterKey
                ? "cursor-pointer hover:border-slate-500 hover:scale-[1.02]"
                : ""
            } ${isSelected ? "ring-2 ring-rose-500 border-rose-500" : ""}`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400 tracking-wide uppercase">
                {card.label}
              </span>
              <div className={`p-1.5 rounded-lg ${card.iconColor}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline justify-between">
              <div className="text-2xl font-bold font-mono tracking-tight">
                {card.value}
              </div>
              {card.badge && (
                <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  {card.badge}
                </span>
              )}
            </div>

            <div className="mt-1 text-[11px] text-slate-400 truncate">
              {card.sub}
            </div>
          </div>
        );
      })}
    </div>
  );
}
