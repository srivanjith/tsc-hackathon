import React, { useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  AlertOctagon,
  Send,
  HelpCircle,
  Eye,
  CheckCircle,
  Clock,
  Filter,
} from "lucide-react";

export default function IncidentQueue({
  incidents = [],
  onSelectIncident,
  onDispatchClick,
  activeFilter = "ALL",
  onFilterChange,
}) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredIncidents = incidents.filter((inc) => {
    // Text search
    const matchesSearch =
      inc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.zone_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.category.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    // Filter by type
    if (activeFilter === "CRITICAL") {
      return inc.rescue_priority_score >= 75.0;
    }
    if (activeFilter === "UNDER_REVIEW") {
      return inc.credibility_score < 0.5;
    }
    if (activeFilter === "DISPATCHED") {
      return inc.status === "DISPATCHED";
    }
    if (activeFilter === "VERIFIED") {
      return inc.verified === true && inc.credibility_score >= 0.5;
    }
    return true;
  });

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 shadow-xl flex flex-col h-[520px]">
      {/* Header and Filter Tabs */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h3 className="font-bold text-slate-100 flex items-center gap-2">
            <span>Rescue Priority Queue</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
              {filteredIncidents.length}
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Ranked by Urgency × Credibility Trust Factor
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => onFilterChange("ALL")}
            className={`px-2.5 py-1 rounded font-medium transition ${
              activeFilter === "ALL"
                ? "bg-slate-800 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            All
          </button>
          <button
            onClick={() => onFilterChange("CRITICAL")}
            className={`px-2.5 py-1 rounded font-medium transition ${
              activeFilter === "CRITICAL"
                ? "bg-rose-900/60 text-rose-300 shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Critical (≥75)
          </button>
          <button
            onClick={() => onFilterChange("UNDER_REVIEW")}
            className={`px-2.5 py-1 rounded font-medium transition ${
              activeFilter === "UNDER_REVIEW"
                ? "bg-purple-900/60 text-purple-300 shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Under Review
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="pt-3 pb-2">
        <input
          type="text"
          placeholder="Filter by zone, keyword, or threat type..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-1.5 text-xs rounded-lg bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition"
        />
      </div>

      {/* Incident List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {filteredIncidents.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No incidents match the selected filter.
          </div>
        ) : (
          filteredIncidents.map((incident, index) => {
            const isCritical = incident.rescue_priority_score >= 75;
            const isHeld = incident.credibility_score < 0.5;
            const trustPct = Math.round(incident.credibility_score * 100);

            return (
              <div
                key={incident.id}
                className={`p-3 rounded-xl border transition-all duration-150 ${
                  isHeld
                    ? "bg-purple-950/20 border-purple-900/50 hover:border-purple-700"
                    : isCritical
                    ? "bg-rose-950/20 border-rose-900/50 hover:border-rose-700"
                    : "bg-slate-950/40 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-slate-500">
                      #{index + 1}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase tracking-wide">
                      {incident.category}
                    </span>
                    <span className="text-xs text-slate-400 truncate max-w-[120px]">
                      {incident.zone_name}
                    </span>
                  </div>

                  {/* Priority and Trust Badges */}
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                        isCritical
                          ? "bg-rose-600 text-white"
                          : isHeld
                          ? "bg-purple-800 text-purple-200"
                          : "bg-amber-600 text-white"
                      }`}
                    >
                      Score {Math.round(incident.rescue_priority_score)}
                    </span>
                  </div>
                </div>

                {/* Title */}
                <h4 className="text-xs font-bold text-slate-100 mt-1.5 leading-snug">
                  {incident.title}
                </h4>

                {/* Metrics Pill */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 pt-2 border-t border-slate-800/80">
                  <div className="flex items-center gap-3">
                    <span>
                      Sev: <strong className="text-slate-200">{incident.severity}/5</strong>
                    </span>
                    <span>
                      Risk: <strong className="text-slate-200">~{incident.affected_population}</strong>
                    </span>
                    <span className="flex items-center gap-1 font-mono">
                      Trust:{" "}
                      <strong
                        className={
                          trustPct >= 70
                            ? "text-emerald-400"
                            : trustPct >= 50
                            ? "text-amber-400"
                            : "text-purple-400"
                        }
                      >
                        {trustPct}%
                      </strong>
                    </span>
                  </div>

                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                      incident.status === "DISPATCHED"
                        ? "bg-blue-900/60 text-blue-300"
                        : isHeld
                        ? "bg-purple-900/60 text-purple-300"
                        : "bg-emerald-900/60 text-emerald-300"
                    }`}
                  >
                    {incident.status}
                  </span>
                </div>

                {/* Action Row */}
                <div className="flex items-center justify-end gap-2 mt-2 pt-1">
                  <button
                    onClick={() => onSelectIncident(incident)}
                    className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-800 transition"
                  >
                    <HelpCircle className="w-3 h-3 text-rose-400" />
                    <span>Explain Math</span>
                  </button>

                  <button
                    onClick={() => onDispatchClick(incident)}
                    className="flex items-center gap-1 text-[11px] text-white px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-500 font-semibold shadow-sm transition"
                  >
                    <Send className="w-3 h-3" />
                    <span>Dispatch</span>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
