import React from "react";
import {
  ShieldAlert,
  Activity,
  Route,
  Radio,
  FileText,
  PlusCircle,
  RefreshCw,
  SlidersHorizontal,
} from "lucide-react";

export default function Navbar({
  onOpenReportModal,
  onOpenRoadModal,
  onOpenSensorModal,
  onOpenSitRepModal,
  onRefresh,
  isRefreshing,
}) {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 to-amber-500 flex items-center justify-center shadow-lg shadow-rose-900/40">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white font-mono">
                  ResQ<span className="text-rose-500">Trust</span>
                </span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-950 text-emerald-400 border border-emerald-800/80">
                  v2.4 LIVE
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Trust-Centric Disaster Response & Dynamic Replanning
              </p>
            </div>
          </div>

          {/* Real-time Status Badges */}
          <div className="hidden lg:flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
              <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span>Trust Engine:</span>
              <span className="text-emerald-400 font-medium">Filtering Active</span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
              <Route className="w-3.5 h-3.5 text-cyan-400" />
              <span>Replanner:</span>
              <span className="text-cyan-400 font-medium">NetworkX Active</span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
              <Radio className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
              <span>Sensors:</span>
              <span className="text-amber-400 font-medium">IoT Synced</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenReportModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md shadow-rose-900/30 transition"
              title="Ingest new citizen/sensor report"
            >
              <PlusCircle className="w-4 h-4" />
              <span>New Report</span>
            </button>

            <button
              onClick={onOpenRoadModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 hover:text-amber-300 border border-amber-900/50 text-xs font-medium transition"
              title="Simulate road blockages and live route replanning"
            >
              <Route className="w-4 h-4" />
              <span className="hidden sm:inline">Simulate Hazard</span>
            </button>

            <button
              onClick={onOpenSensorModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 hover:text-cyan-300 border border-cyan-900/50 text-xs font-medium transition"
              title="Inspect and simulate IoT sensor streams"
            >
              <Radio className="w-4 h-4" />
              <span className="hidden sm:inline">IoT Sensors</span>
            </button>

            <button
              onClick={onOpenSitRepModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
              title="Generate Operational Situation Report"
            >
              <FileText className="w-4 h-4" />
              <span className="hidden md:inline">SitRep</span>
            </button>

            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className={`p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition ${
                isRefreshing ? "opacity-50 cursor-not-allowed" : ""
              }`}
              title="Refresh telemetry"
            >
              <RefreshCw
                className={`w-4 h-4 ${isRefreshing ? "animate-spin text-rose-400" : ""}`}
              />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
