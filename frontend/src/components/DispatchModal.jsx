import React, { useState } from "react";
import { X, Send, Navigation, Clock, ShieldCheck, Check } from "lucide-react";
import { api } from "../api";

export default function DispatchModal({
  incident,
  resources = [],
  onClose,
  onDispatchSuccess,
}) {
  const [selectedUnitId, setSelectedUnitId] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (!incident) return null;

  const availableUnits = resources.filter((u) => u.status === "AVAILABLE");

  // Determine recommended unit based on incident category
  const isFlood = incident.category.toLowerCase().includes("flood");
  const recommendedUnit = availableUnits.find((u) =>
    isFlood ? u.unit_type === "EVAC_BOAT" : u.unit_type === "SEARCH_RESCUE"
  ) || availableUnits[0];

  const handleDispatch = async () => {
    setIsSubmitting(true);
    setError("");
    try {
      const unitToDispatch = selectedUnitId || (recommendedUnit ? recommendedUnit.id : null);
      const res = await api.dispatchResource(incident.id, unitToDispatch);
      onDispatchSuccess && onDispatchSuccess(res);
      onClose();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to dispatch unit. All units may be deployed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs px-2 py-0.5 rounded font-bold bg-rose-950 text-rose-300 border border-rose-800">
                Priority: {Math.round(incident.rescue_priority_score)}/100
              </span>
              <span className="text-xs text-slate-400">
                Near {incident.nearest_junction}
              </span>
            </div>
            <h2 className="text-base font-bold text-white">
              Dispatch Resource: {incident.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          <p className="text-xs text-slate-400">
            ResQTrust's Greedy Allocation Engine computes the closest available team with the appropriate capability profile for this zone.
          </p>

          {error && (
            <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-200 text-xs">
              {error}
            </div>
          )}

          {/* Unit Selection Options */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">
              Select Responding Unit:
            </label>

            {availableUnits.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-amber-400 text-center">
                All teams are currently deployed on active missions. Free a unit or reassign.
              </div>
            ) : (
              availableUnits.map((unit) => {
                const isRecommended = recommendedUnit?.id === unit.id;
                const isChosen =
                  selectedUnitId === unit.id || (!selectedUnitId && isRecommended);

                return (
                  <div
                    key={unit.id}
                    onClick={() => setSelectedUnitId(unit.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between text-xs ${
                      isChosen
                        ? "bg-slate-800 border-rose-500 ring-1 ring-rose-500"
                        : "bg-slate-950 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-200">
                          {unit.name}
                        </span>
                        {isRecommended && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                            Recommended Match
                          </span>
                        )}
                      </div>
                      <div className="text-slate-400 mt-0.5">
                        {unit.unit_type} • Station: Node {unit.current_junction} • Capacity: {unit.capacity}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-cyan-400">
                        Available
                      </span>
                      {isChosen && <Check className="w-4 h-4 text-rose-400" />}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
            <div className="flex items-center justify-between">
              <span>Target Destination:</span>
              <strong className="text-slate-200">
                {incident.zone_name} (Node {incident.nearest_junction})
              </strong>
            </div>
            <div className="flex items-center justify-between">
              <span>Route Optimization:</span>
              <strong className="text-cyan-400">
                NetworkX Dijkstra Shortest Path
              </strong>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
          >
            Cancel
          </button>
          <button
            onClick={handleDispatch}
            disabled={isSubmitting || availableUnits.length === 0}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-900/40 transition disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span>{isSubmitting ? "Dispatching..." : "Confirm & Route Squad"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
