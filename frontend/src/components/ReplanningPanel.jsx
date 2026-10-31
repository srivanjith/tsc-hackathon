import React, { useState } from "react";
import {
  Route,
  AlertTriangle,
  ArrowRight,
  CheckCircle,
  RefreshCw,
  Clock,
  ShieldCheck,
  Zap,
  Navigation,
} from "lucide-react";
import { blockRoad, unblockRoad, replan, approveDecision } from "../services/api";

export default function ReplanningPanel({
  roads = [],
  assignments = [],
  onStateChanged,
}) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [replanData, setReplanData] = useState(null);
  const [approvalStatus, setApprovalStatus] = useState("");

  const handleToggleRoad = async (road, customReason) => {
    setIsProcessing(true);
    try {
      if (road.blocked) {
        await unblockRoad(road.id);
      } else {
        await blockRoad(
          road.id,
          customReason || `Severe hazard disruption across ${road.highway_code || "arterial"} corridor`
        );
      }
      // Trigger dynamic RippleGuard replanning
      const rep = await replan();
      setReplanData(rep.data);
      setApprovalStatus("");
      onStateChanged && onStateChanged();
    } catch (err) {
      console.error("Road toggle error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApprove = async () => {
    if (!replanData?.decision_log_id) return;
    setIsProcessing(true);
    try {
      await approveDecision(replanData.decision_log_id);
      setApprovalStatus("APPROVED");
      onStateChanged && onStateChanged();
    } catch (err) {
      console.error("Approval error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Find strategic presets
  const nh7Himalayan = roads.find(
    (r) => (r.from_node === "Delhi" && r.to_node === "Dehradun") || (r.from_node === "Dehradun" && r.to_node === "Delhi")
  );
  const nh27Assam = roads.find(
    (r) => (r.from_node === "Patna" && r.to_node === "Guwahati") || (r.from_node === "Guwahati" && r.to_node === "Patna")
  );
  const nh16Coastal = roads.find(
    (r) => (r.from_node === "Kolkata" && r.to_node === "Bhubaneswar") || (r.from_node === "Bhubaneswar" && r.to_node === "Kolkata")
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Route className="w-5 h-5 text-[#1677D2]" />
              <h2 className="text-base font-bold text-slate-800">
                RippleGuard™ Dynamic Corridor Replanning & Resilience Engine
              </h2>
            </div>
            <p className="text-xs text-slate-500 max-w-3xl">
              When a National Highway corridor collapses from landslides, river surges, or cyclonic gales, RippleGuard doesn't merely find a line on a map — it pinpoints affected strategic missions, audits remaining battalion capacity, evaluates isolated unmet demand, and produces an explainable revised deployment for human commander approval.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-blue-50 text-[#1677D2] border border-blue-200 font-bold">
              NetworkX Deterministic Routing
            </span>
          </div>
        </div>

        {/* Quick Simulation Presets */}
        <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-3">
          <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-amber-500" />
            Quick Disaster Scenarios:
          </span>

          {nh7Himalayan && (
            <button
              onClick={() => handleToggleRoad(nh7Himalayan, "Chamoli Earthquake Rockfall Severing NH7 Himalayan Pass")}
              disabled={isProcessing}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition shadow-sm flex items-center gap-1.5 ${
                nh7Himalayan.blocked ? "bg-[#16A36A] hover:bg-emerald-600" : "bg-[#DC3545] hover:bg-red-600"
              }`}
            >
              <span>{nh7Himalayan.blocked ? "Reopen NH7 Himalayan Pass" : "Simulate NH7 Debris Rockfall (Delhi ↔ Dehradun)"}</span>
            </button>
          )}

          {nh27Assam && (
            <button
              onClick={() => handleToggleRoad(nh27Assam, "Brahmaputra River Inundation Breach over NH27 Lifeline")}
              disabled={isProcessing}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition shadow-sm flex items-center gap-1.5 ${
                nh27Assam.blocked ? "bg-[#16A36A] hover:bg-emerald-600" : "bg-indigo-600 hover:bg-indigo-700"
              }`}
            >
              <span>{nh27Assam.blocked ? "Reopen NH27 Lifeline" : "Simulate NH27 River Surge (Patna ↔ Guwahati)"}</span>
            </button>
          )}

          {nh16Coastal && (
            <button
              onClick={() => handleToggleRoad(nh16Coastal, "Super Cyclone Storm Surge Breach over NH16 Coastal Trunk")}
              disabled={isProcessing}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition shadow-sm flex items-center gap-1.5 ${
                nh16Coastal.blocked ? "bg-[#16A36A] hover:bg-emerald-600" : "bg-purple-600 hover:bg-purple-700"
              }`}
            >
              <span>{nh16Coastal.blocked ? "Reopen NH16 Coastal" : "Simulate NH16 Cyclone Inundation (Kolkata ↔ Bhubaneswar)"}</span>
            </button>
          )}
        </div>
      </div>

      {/* Rerouted Missions & Side-by-side Route Comparison */}
      {replanData && (replanData.affected_missions?.length > 0 || replanData.affected_assignments?.length > 0) && (
        <div className="bg-white rounded-xl border border-amber-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#F59E0B] animate-ping"></span>
              <h3 className="font-bold text-slate-900 text-sm">
                RippleGuard Detour Plan: {(replanData.affected_missions || replanData.affected_assignments || []).length} Strategic Mission(s) Rerouted
              </h3>
            </div>
            <span className="text-[11px] font-mono font-bold text-[#F59E0B] px-2.5 py-1 rounded bg-amber-50 border border-amber-200">
              Human Commander Authorization Required
            </span>
          </div>

          <div className="space-y-3">
            {(replanData.affected_missions || replanData.affected_assignments || []).map((rev, i) => (
              <div
                key={i}
                className="p-4 rounded-xl bg-[#F5F8FC] border border-slate-200 space-y-3 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="font-bold text-slate-800 text-sm flex items-center gap-2">
                    <Navigation className="w-4 h-4 text-[#1677D2]" />
                    <span>{rev.resource_name} → {rev.incident_title}</span>
                  </div>
                  <span className="text-[11px] font-semibold text-slate-500">
                    Mission #{rev.assignment_id} {rev.state ? `• ${rev.state}` : ""}
                  </span>
                </div>

                {/* Side-by-side Route Comparison */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Previous severed highway route */}
                  <div className="p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-900 space-y-1.5">
                    <div className="flex items-center justify-between font-semibold text-[11px]">
                      <span className="flex items-center gap-1.5 text-[#DC3545]">
                        <span className="w-2 h-2 rounded-full bg-[#DC3545]"></span>
                        Previous Severed Corridor:
                      </span>
                      <span className="font-mono">{rev.old_time_hours || rev.old_travel_time} hrs</span>
                    </div>
                    <div className="font-mono text-xs line-through text-red-700">
                      {(rev.old_route || []).join(" → ")}
                    </div>
                  </div>

                  {/* Newly calculated alternate detour */}
                  <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 space-y-1.5">
                    <div className="flex items-center justify-between font-semibold text-[11px]">
                      <span className="flex items-center gap-1.5 text-[#16A36A]">
                        <span className="w-2 h-2 rounded-full bg-[#16A36A] animate-pulse"></span>
                        RippleGuard Optimal National Detour:
                      </span>
                      <span className="font-mono font-bold text-[#16A36A]">
                        {rev.new_time_hours || rev.new_travel_time} hrs {rev.detour_km ? `(${rev.detour_km} km)` : ""}
                      </span>
                    </div>
                    <div className="font-mono text-xs font-bold text-emerald-800">
                      {(rev.new_route || []).join(" → ")}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Unmet Needs info */}
          {replanData.total_unmet_people > 0 && (
            <div className="p-3.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-center justify-between">
              <span>
                <strong>⚠️ Isolated Hotspots:</strong> {replanData.total_unmet_people.toLocaleString()} citizens cut off from land transport. Immediate tactical airlift (IAF / Coast Guard) recommended.
              </span>
            </div>
          )}

          {/* Commander Approval Trigger */}
          <div className="pt-2 flex items-center justify-end gap-3">
            {approvalStatus === "APPROVED" ? (
              <div className="flex items-center gap-2 text-xs font-bold text-[#16A36A] bg-emerald-50 px-4 py-2.5 rounded-lg border border-emerald-200">
                <CheckCircle className="w-4 h-4" />
                <span>Revised Plan Authorized & Relayed to NDRF Tactical Command</span>
              </div>
            ) : (
              <button
                onClick={handleApprove}
                disabled={isProcessing}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#16A36A] hover:bg-emerald-600 text-white text-xs font-bold shadow-md transition disabled:opacity-50"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Authorize Revised Plan (Commander Sign-Off)</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Roads List across India */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700 flex items-center justify-between">
          <span>National Highway Corridors ({roads.length} Arterials)</span>
          <span className="text-[11px] text-slate-400 font-normal">
            Click any highway to simulate disaster blockage or landslide
          </span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {roads.map((road) => (
            <div
              key={road.id}
              className={`p-3 rounded-xl border flex flex-col justify-between text-xs transition ${
                road.blocked
                  ? "bg-red-50/70 border-red-200 text-red-900"
                  : "bg-[#F5F8FC] border-slate-200 text-slate-800"
              }`}
            >
              <div className="mb-2">
                <div className="font-bold flex items-center justify-between gap-2">
                  <span className="truncate">{road.road_name || `${road.from_node} ↔ ${road.to_node}`}</span>
                  {road.blocked && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#DC3545] text-white font-bold shrink-0">
                      BLOCKED
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">
                  {road.highway_code || "NH"} • {road.distance_km} km ({road.travel_time}m) • {road.state}
                </div>
                {road.blocked && (
                  <div className="text-[10px] text-red-700 font-medium mt-1">
                    Cause: {road.block_reason || "Severe debris obstruction"}
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end">
                <button
                  onClick={() => handleToggleRoad(road)}
                  disabled={isProcessing}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                    road.blocked
                      ? "bg-[#16A36A] hover:bg-emerald-600 text-white"
                      : "bg-white hover:bg-slate-100 text-[#DC3545] border border-red-200"
                  }`}
                >
                  {road.blocked ? "Reopen Corridor" : "Simulate Blockage"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
