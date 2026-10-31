import React, { useState } from "react";
import {
  Layers,
  Home,
  LifeBuoy,
  Ambulance,
  Truck,
  CheckCircle,
  Play,
  AlertTriangle,
  MapPin,
  ShieldAlert,
} from "lucide-react";
import { generatePlan } from "../services/api";

export default function ResourcePanel({
  resources = [],
  shelters = [],
  assignments = [],
  onPlanGenerated,
}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [planResult, setPlanResult] = useState(null);

  const handleGeneratePlan = async () => {
    setIsGenerating(true);
    try {
      const res = await generatePlan();
      setPlanResult(res.data);
      onPlanGenerated && onPlanGenerated();
    } catch (err) {
      console.error("Plan generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Trigger */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Layers className="w-5 h-5 text-[#1677D2]" />
            <h2 className="text-base font-bold text-slate-800">
              National Defense, NDRF & Humanitarian Evacuation Fleet
            </h2>
          </div>
          <p className="text-xs text-slate-500">
            Greedy allocation engine matches prioritized multi-hazard zones across India with specialized battalions (NDRF, IAF tactical airlift, Indian Coast Guard flotillas, and SDRF divisions).
          </p>
        </div>

        <button
          onClick={handleGeneratePlan}
          disabled={isGenerating}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#1677D2] text-white text-xs font-semibold hover:bg-blue-600 transition shadow-sm disabled:opacity-50"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>{isGenerating ? "Calculating Corridor Allocations..." : "Run National Multi-Hazard Allocation"}</span>
        </button>
      </div>

      {planResult && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs text-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-[#1677D2]" />
            <span>
              <strong>Strategic Allocation Mobilized:</strong>{" "}
              {planResult.allocated_assignments?.length} national missions dispatched across highway corridors.
            </span>
          </div>
          <span className="px-2 py-0.5 rounded bg-blue-200 text-blue-800 font-bold text-[10px]">
            Decision #{planResult.decision_log_id} Logged
          </span>
        </div>
      )}

      {/* Grid: Resources Left | Shelters Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Resources */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700 flex items-center justify-between">
            <span>Specialized Defense & Relief Battalions ({resources.length})</span>
            <span className="text-[11px] text-slate-400 font-normal">Pan-India Bases</span>
          </h3>

          <div className="space-y-2.5">
            {resources.map((res) => {
              let symbol = "🛡️";
              let badgeColor = "bg-blue-50 text-[#1677D2]";
              const t = (res.type || "").toUpperCase();

              if (t.includes("AIRLIFT") || t.includes("IAF")) {
                symbol = "🚁";
                badgeColor = "bg-indigo-50 text-indigo-700";
              } else if (t.includes("BOAT") || t.includes("FLOTILLA")) {
                symbol = "🚤";
                badgeColor = "bg-cyan-50 text-cyan-700";
              } else if (t.includes("EARTHMOVER")) {
                symbol = "🚜";
                badgeColor = "bg-amber-50 text-amber-700";
              } else if (t.includes("NDRF")) {
                symbol = "🎖️";
                badgeColor = "bg-emerald-50 text-emerald-700";
              }

              return (
                <div
                  key={res.id}
                  className="p-3 rounded-lg border border-slate-100 bg-[#F5F8FC] flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg text-base ${badgeColor}`}>
                      <span>{symbol}</span>
                    </div>
                    <div>
                      <div className="font-bold text-slate-800">{res.name}</div>
                      <div className="text-[11px] text-slate-500 flex items-center gap-1.5 mt-0.5">
                        <span className="font-mono">{res.type}</span>
                        {res.state && (
                          <span className="text-slate-400">• {res.state} ({res.district})</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="font-bold font-mono text-[#1677D2] text-sm">
                      {res.available_units}
                    </div>
                    <div className="text-[10px] text-slate-400">Available Squadrons</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Shelters */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700 flex items-center justify-between">
            <span>District Evacuation Shelters & Stadiums ({shelters.length})</span>
            <span className="text-[11px] text-slate-400 font-normal">Capacities</span>
          </h3>

          <div className="space-y-2.5">
            {shelters.map((s) => {
              const remaining = s.capacity - s.occupancy;
              const occPct = Math.round((s.occupancy / s.capacity) * 100);

              return (
                <div
                  key={s.id}
                  className="p-3 rounded-lg border border-slate-100 bg-[#F5F8FC] space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <Home className="w-4 h-4 text-[#16A36A]" />
                        <span className="font-bold text-slate-800">{s.name}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 ml-6">
                        {s.state} • {s.district}
                      </div>
                    </div>
                    <span className="font-mono text-[11px] font-bold text-slate-700">
                      {s.occupancy.toLocaleString()} / {s.capacity.toLocaleString()} ({occPct}%)
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        occPct > 80
                          ? "bg-[#DC3545]"
                          : occPct > 50
                          ? "bg-[#F59E0B]"
                          : "bg-[#16A36A]"
                      }`}
                      style={{ width: `${occPct}%` }}
                    ></div>
                  </div>

                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Occupancy: {s.occupancy.toLocaleString()} evacuees</span>
                    <span className="text-[#16A36A] font-semibold">
                      Remaining Capacity: {remaining.toLocaleString()}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
