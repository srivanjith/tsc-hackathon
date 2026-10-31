import React, { useEffect, useState } from "react";
import {
  X,
  FileText,
  Printer,
  Download,
  ShieldCheck,
  ShieldAlert,
  Route,
  CheckCircle,
} from "lucide-react";
import { api } from "../api";

export default function SituationReportModal({ onClose }) {
  const [sitrep, setSitrep] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getSitRep()
      .then((data) => {
        setSitrep(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load sitrep", err);
        setLoading(false);
      });
  }, []);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-600/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase">
                Official Operational SitRep
              </span>
              <h2 className="text-base font-bold text-white mt-0.5">
                ResQTrust Situation Report & Audit Trail
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / PDF</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* SitRep Document Content */}
        <div className="p-6 flex-1 overflow-y-auto space-y-5 text-xs text-slate-300 font-sans">
          {loading ? (
            <div className="text-center py-12 text-slate-500">
              Generating Situation Report...
            </div>
          ) : sitrep ? (
            <>
              {/* Executive Summary Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 text-[11px]">
                    Total Reported:
                  </span>
                  <div className="text-xl font-bold font-mono text-white">
                    {sitrep.summary.total_incidents}
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 text-[11px]">
                    Critical Threats:
                  </span>
                  <div className="text-xl font-bold font-mono text-rose-400">
                    {sitrep.summary.critical_priority_threats}
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 text-[11px]">
                    False Alarms Held:
                  </span>
                  <div className="text-xl font-bold font-mono text-emerald-400">
                    {sitrep.summary.false_alarms_held}
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 text-[11px]">
                    Active Missions:
                  </span>
                  <div className="text-xl font-bold font-mono text-cyan-400">
                    {sitrep.summary.active_deployments}
                  </div>
                </div>
              </div>

              {/* Critical Hotspots Table */}
              <div className="space-y-2">
                <h3 className="font-bold text-slate-200 text-xs uppercase tracking-wide">
                  1. High Priority Disaster Zones
                </h3>
                <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                        <th className="p-2.5">Zone & Incident</th>
                        <th className="p-2.5 text-center">Score</th>
                        <th className="p-2.5 text-center">Credibility</th>
                        <th className="p-2.5">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {sitrep.critical_hotspots.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/50">
                          <td className="p-2.5">
                            <div className="font-semibold text-slate-100">
                              {item.title}
                            </div>
                            <div className="text-[11px] text-slate-400">
                              {item.zone}
                            </div>
                          </td>
                          <td className="p-2.5 text-center font-mono font-bold text-rose-400">
                            {Math.round(item.score)}/100
                          </td>
                          <td className="p-2.5 text-center font-mono text-emerald-400">
                            {item.credibility}%
                          </td>
                          <td className="p-2.5">
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300">
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Blocked Infrastructure Table */}
              <div className="space-y-2">
                <h3 className="font-bold text-slate-200 text-xs uppercase tracking-wide">
                  2. Infrastructure Impairments & Road Closures
                </h3>
                {sitrep.blocked_infrastructure.length === 0 ? (
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-emerald-400 text-center">
                    All major arterial routes and bridges are currently open.
                  </div>
                ) : (
                  <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                          <th className="p-2.5">Arterial Corridor</th>
                          <th className="p-2.5">Junctions</th>
                          <th className="p-2.5">Obstruction Reason</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80">
                        {sitrep.blocked_infrastructure.map((road, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/50">
                            <td className="p-2.5 font-bold text-rose-300">
                              {road.road}
                            </td>
                            <td className="p-2.5 font-mono text-slate-400">
                              {road.junctions}
                            </td>
                            <td className="p-2.5 text-slate-300">
                              {road.reason || "Hazard debris"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Active Missions */}
              <div className="space-y-2">
                <h3 className="font-bold text-slate-200 text-xs uppercase tracking-wide">
                  3. Field Deployments & Mission Routing
                </h3>
                <div className="space-y-2">
                  {sitrep.active_missions.map((m) => (
                    <div
                      key={m.id}
                      className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-bold text-slate-200">
                          {m.unit} → {m.incident}
                        </div>
                        <div className="text-[11px] text-slate-400">
                          ETA: {m.eta_minutes} min • Status:{" "}
                          <span className="font-semibold text-cyan-400">
                            {m.status}
                          </span>
                        </div>
                      </div>
                      {m.detour_active && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
                          ⚡ Dynamic Detour Active
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <span>
            Verified by ResQTrust Evidence Intelligence & Routing Engine.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
