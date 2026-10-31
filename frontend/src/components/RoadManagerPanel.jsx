import React, { useState } from "react";
import {
  X,
  Route,
  AlertTriangle,
  CheckCircle,
  Flame,
  Zap,
  RefreshCw,
} from "lucide-react";
import { api } from "../api";

export default function RoadManagerPanel({
  roads = [],
  junctions = {},
  onClose,
  onRoadUpdated,
}) {
  const [loadingRoadId, setLoadingRoadId] = useState(null);

  const handleToggle = async (road, block, reason = "Flood debris & structural failure") => {
    setLoadingRoadId(road.id);
    try {
      await api.toggleRoad(road.id, block, reason);
      onRoadUpdated && onRoadUpdated();
    } catch (err) {
      console.error("Failed to toggle road status", err);
    } finally {
      setLoadingRoadId(null);
    }
  };

  const handlePreset = async (u, v, reason) => {
    const road = roads.find(
      (r) => (r.u === u && r.v === v) || (r.u === v && r.v === u)
    );
    if (road) {
      await handleToggle(road, !road.is_blocked, reason);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 uppercase">
                Interactive Simulation Control
              </span>
            </div>
            <h2 className="text-base font-bold text-white mt-1">
              Road Hazard & Dynamic Routing Simulator
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Block any arterial corridor to demonstrate live NetworkX route replanning and visual diff to the jury.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Presets */}
        <div className="p-4 bg-slate-950/70 border-b border-slate-800 flex flex-wrap gap-2 text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1 self-center mr-1">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            Quick Scenarios:
          </span>
          <button
            onClick={() =>
              handlePreset(
                "J2",
                "J3",
                "Flash flood inundation (4.4m) over Riverside Causeway"
              )
            }
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            Toggle J2 ↔ J3 (Riverside Causeway)
          </button>
          <button
            onClick={() =>
              handlePreset(
                "J3",
                "J7",
                "Grand River Bridge structural cable displacement"
              )
            }
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            Toggle J3 ↔ J7 (Grand River Bridge)
          </button>
          <button
            onClick={() =>
              handlePreset(
                "J4",
                "J5",
                "Mudslide debris covering commercial corridor"
              )
            }
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            Toggle J4 ↔ J5 (Commercial Link)
          </button>
        </div>

        {/* Roads Grid */}
        <div className="p-5 flex-1 overflow-y-auto space-y-2.5">
          {roads.map((road) => {
            const isLoading = loadingRoadId === road.id;
            const uName = junctions[road.u]?.name || road.u;
            const vName = junctions[road.v]?.name || road.v;

            return (
              <div
                key={road.id}
                className={`p-3 rounded-xl border flex items-center justify-between text-xs transition ${
                  road.is_blocked
                    ? "bg-rose-950/30 border-rose-800 text-rose-200"
                    : "bg-slate-950 border-slate-800 text-slate-300"
                }`}
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-100">
                      {road.road_name}
                    </span>
                    <span className="font-mono text-[10px] text-slate-400">
                      [{road.u} ↔ {road.v}]
                    </span>
                    {road.is_blocked && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-900 text-rose-200 font-bold">
                        BLOCKED
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {uName} to {vName} • {road.distance_km} km @ {road.base_speed_kmh} km/h
                  </div>
                  {road.is_blocked && road.blockage_reason && (
                    <div className="text-[11px] text-rose-400 font-medium">
                      Obstruction: {road.blockage_reason}
                    </div>
                  )}
                </div>

                <button
                  onClick={() =>
                    handleToggle(
                      road,
                      !road.is_blocked,
                      road.is_blocked
                        ? null
                        : "Flood inundation and debris blockage"
                    )
                  }
                  disabled={isLoading}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition flex items-center gap-1.5 ${
                    road.is_blocked
                      ? "bg-emerald-600 hover:bg-emerald-500 text-white"
                      : "bg-rose-600 hover:bg-rose-500 text-white"
                  }`}
                >
                  {isLoading ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : road.is_blocked ? (
                    <>
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Reopen Road</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>Block Road</span>
                    </>
                  )}
                </button>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
