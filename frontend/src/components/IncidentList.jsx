import React from "react";
import { ShieldAlert, AlertTriangle, Users, Clock, Eye, MapPin } from "lucide-react";

const getHazardEmoji = (type = "") => {
  const t = type.toLowerCase();
  if (t.includes("cyclone")) return "🌀";
  if (t.includes("earthquake") || t.includes("seismic")) return "🌋";
  if (t.includes("landslide")) return "🏔️";
  if (t.includes("fire")) return "🔥";
  return "🌊";
};

export default function IncidentList({ incidents = [], onSelectIncident, selectedIncident }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col h-[540px]">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
            <span>Prioritized Incident Stream</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-[#1677D2] font-mono font-bold">
              {incidents.length}
            </span>
          </h3>
          <p className="text-[11px] text-slate-400">
            Random Forest ML + Formula: P = 0.35S + 0.25U + 0.25I + 0.15R
          </p>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-50 text-[#DC3545] border border-red-200 uppercase">
          SIMULATION
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2.5 pt-3 pr-1">
        {incidents.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">
            No active incidents matching criteria.
          </div>
        ) : (
          incidents.map((incident, idx) => {
            const isCrit = incident.priority_score >= 80 || incident.predicted_risk_level === "CRITICAL";
            const isSelected = selectedIncident?.id === incident.id;
            const emoji = getHazardEmoji(incident.type);

            return (
              <div
                key={incident.id}
                onClick={() => onSelectIncident && onSelectIncident(incident)}
                className={`p-3 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? "border-[#1677D2] bg-blue-50/40 shadow-sm ring-1 ring-blue-400/40"
                    : isCrit
                    ? "border-red-100 bg-red-50/20 hover:border-red-300"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="font-mono text-xs font-bold text-slate-400">
                      #{idx + 1}
                    </span>
                    <span className="text-sm">{emoji}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded font-semibold bg-slate-100 text-slate-700">
                      {incident.type}
                    </span>
                    {incident.state && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded font-semibold bg-blue-50 text-blue-700 flex items-center gap-0.5">
                        <MapPin className="w-2.5 h-2.5" />
                        {incident.state}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    {incident.predicted_risk_level && (
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                          incident.predicted_risk_level === "CRITICAL"
                            ? "bg-red-900 text-white"
                            : incident.predicted_risk_level === "HIGH"
                            ? "bg-amber-600 text-white"
                            : "bg-blue-600 text-white"
                        }`}
                      >
                        {incident.predicted_risk_level}
                      </span>
                    )}
                    <span
                      className={`font-mono text-xs font-bold px-2 py-0.5 rounded ${
                        isCrit
                          ? "bg-[#DC3545] text-white"
                          : "bg-[#F59E0B] text-white"
                      }`}
                    >
                      P: {Math.round(incident.priority_score)}
                    </span>
                  </div>
                </div>

                <h4 className="font-bold text-xs text-slate-900 mt-1.5 leading-snug">
                  {incident.title}
                </h4>

                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100">
                  <div className="flex items-center gap-3">
                    <span>Sev: <strong className="text-slate-700">{incident.severity}/5</strong></span>
                    <span>Urg: <strong className="text-slate-700">{incident.urgency}/5</strong></span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3 text-slate-400" />
                      ~{incident.affected_people}
                    </span>
                  </div>

                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                      incident.status === "ALLOCATED"
                        ? "bg-blue-100 text-[#1677D2]"
                        : incident.status === "APPROVED"
                        ? "bg-emerald-100 text-[#16A36A]"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {incident.status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
