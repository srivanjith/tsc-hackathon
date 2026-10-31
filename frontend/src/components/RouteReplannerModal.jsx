import React, { useState } from "react";
import {
  X,
  Route,
  AlertTriangle,
  ArrowRight,
  Clock,
  CheckCircle2,
  ShieldAlert,
} from "lucide-react";
import { api } from "../api";

export default function RouteReplannerModal({
  assignment,
  onClose,
  onApprovalSuccess,
}) {
  const [isApproving, setIsApproving] = useState(false);

  if (!assignment) return null;

  const origNodes = assignment.original_route_nodes || [];
  const currNodes = assignment.current_route_nodes || [];
  const origEta = assignment.original_eta_minutes;
  const currEta = assignment.current_eta_minutes;
  const etaDiff = (currEta - origEta).toFixed(1);

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      await api.approveAssignment(assignment.id);
      onApprovalSuccess && onApprovalSuccess(assignment.id);
      onClose();
    } catch (err) {
      console.error("Failed to approve reroute", err);
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
              <Route className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 uppercase tracking-wide">
                Live Replanning Notice
              </span>
              <h2 className="text-base font-bold text-white mt-1">
                Dynamic Detour Review: Assignment #{assignment.id}
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Obstruction Alert Box */}
          <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-900/60 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="text-xs">
              <div className="font-bold text-rose-200">
                Arterial Path Severed by Hazard
              </div>
              <div className="text-rose-300/90 mt-0.5">
                {assignment.change_reason ||
                  "A road along this unit's route was blocked by debris/flooding. ResQTrust automatically computed an alternative traversable path."}
              </div>
            </div>
          </div>

          {/* Unit & Target Summary */}
          <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950 p-3 rounded-xl border border-slate-800">
            <div>
              <span className="text-slate-500">Field Unit:</span>
              <div className="font-bold text-slate-200">
                {assignment.resource_name || assignment.resource_id}
              </div>
            </div>
            <div>
              <span className="text-slate-500">Incident Target:</span>
              <div className="font-bold text-slate-200 truncate">
                {assignment.incident_title || `Incident #${assignment.incident_id}`}
              </div>
            </div>
          </div>

          {/* Side-by-side Route Comparison */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide">
              Route Path Comparison
            </h4>

            {/* Severed Previous Route */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-rose-950/70 text-xs space-y-1.5">
              <div className="flex items-center justify-between text-slate-400">
                <span className="font-semibold text-rose-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  Previous Severed Route:
                </span>
                <span className="font-mono text-slate-400">{origEta} min</span>
              </div>
              <div className="font-mono text-slate-300 flex items-center flex-wrap gap-1.5 text-xs line-through opacity-75">
                {origNodes.map((node, i) => (
                  <React.Fragment key={`orig-${node}-${i}`}>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-rose-300">
                      {node}
                    </span>
                    {i < origNodes.length - 1 && (
                      <span className="text-slate-600">→</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Alternate Newly Calculated Detour */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-900/70 text-xs space-y-1.5 ring-1 ring-emerald-500/30">
              <div className="flex items-center justify-between text-slate-400">
                <span className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  Optimal Alternative Detour:
                </span>
                <span className="font-mono text-emerald-300 font-bold">
                  {currEta} min ({etaDiff >= 0 ? `+${etaDiff}` : etaDiff} min)
                </span>
              </div>
              <div className="font-mono text-slate-200 flex items-center flex-wrap gap-1.5 text-xs">
                {currNodes.map((node, i) => (
                  <React.Fragment key={`curr-${node}-${i}`}>
                    <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/80 font-bold">
                      {node}
                    </span>
                    {i < currNodes.length - 1 && (
                      <span className="text-emerald-500 font-bold">→</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
          >
            Dismiss
          </button>
          <button
            onClick={handleApprove}
            disabled={isApproving}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-900/40 transition"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>
              {isApproving
                ? "Authorizing..."
                : "Approve Detour & Update Field Unit"}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
