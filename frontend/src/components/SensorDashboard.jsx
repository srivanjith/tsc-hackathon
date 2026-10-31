import React, { useState } from "react";
import {
  X,
  Radio,
  Activity,
  AlertTriangle,
  Zap,
  TrendingUp,
  RefreshCw,
  Waves,
} from "lucide-react";
import { api } from "../api";

export default function SensorDashboard({
  sensors = [],
  onClose,
  onSensorUpdated,
}) {
  const [updatingId, setUpdatingId] = useState(null);

  const handleUpdate = async (sensorId, newValue) => {
    setUpdatingId(sensorId);
    try {
      await api.updateSensor(sensorId, newValue);
      onSensorUpdated && onSensorUpdated();
    } catch (err) {
      console.error("Failed to update sensor reading", err);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[85vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 uppercase">
                Ground Telemetry Network
              </span>
            </div>
            <h2 className="text-base font-bold text-white mt-1">
              IoT Sensor Network & Live Simulation
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Live river depth gauges, seismic accelerometers, and pluviometers cross-referencing incoming reports.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sensor Grid */}
        <div className="p-6 flex-1 overflow-y-auto space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sensors.map((sensor) => {
              const isCrit = sensor.status === "CRITICAL";
              const isWarn = sensor.status === "WARNING";
              const isUpdating = updatingId === sensor.id;

              const pct = Math.min(
                100,
                Math.round((sensor.current_value / (sensor.critical_threshold * 1.3)) * 100)
              );

              return (
                <div
                  key={sensor.id}
                  className={`p-4 rounded-xl border space-y-3 transition ${
                    isCrit
                      ? "bg-rose-950/25 border-rose-800"
                      : isWarn
                      ? "bg-amber-950/25 border-amber-800"
                      : "bg-slate-950 border-slate-800"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <Radio
                          className={`w-4 h-4 ${
                            isCrit
                              ? "text-rose-400 animate-pulse"
                              : isWarn
                              ? "text-amber-400"
                              : "text-emerald-400"
                          }`}
                        />
                        <span className="font-bold text-slate-200 text-xs">
                          {sensor.name}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        {sensor.zone_name} • {sensor.sensor_type}
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        isCrit
                          ? "bg-rose-950 text-rose-300 border border-rose-800"
                          : isWarn
                          ? "bg-amber-950 text-amber-300 border border-amber-800"
                          : "bg-emerald-950 text-emerald-300 border border-emerald-800"
                      }`}
                    >
                      {sensor.status}
                    </span>
                  </div>

                  {/* Value and Gauge */}
                  <div className="space-y-1">
                    <div className="flex items-baseline justify-between text-xs">
                      <span className="text-slate-400">Current Reading:</span>
                      <span
                        className={`text-lg font-mono font-bold ${
                          isCrit
                            ? "text-rose-400"
                            : isWarn
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {sensor.current_value} {sensor.unit}
                      </span>
                    </div>

                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          isCrit
                            ? "bg-rose-500"
                            : isWarn
                            ? "bg-amber-500"
                            : "bg-emerald-500"
                        }`}
                        style={{ width: `${pct}%` }}
                      ></div>
                    </div>

                    <div className="flex justify-between text-[10px] text-slate-500 pt-0.5">
                      <span>Base: {sensor.normal_baseline}</span>
                      <span>Warn: {sensor.warning_threshold}</span>
                      <span>Crit: {sensor.critical_threshold} {sensor.unit}</span>
                    </div>
                  </div>

                  {/* Simulation Controls */}
                  <div className="pt-2 border-t border-slate-800/80 flex items-center gap-2">
                    <button
                      onClick={() =>
                        handleUpdate(
                          sensor.id,
                          parseFloat(
                            (sensor.current_value + (sensor.unit === "Richter" ? 2.5 : 1.5)).toFixed(2)
                          )
                        )
                      }
                      disabled={isUpdating}
                      className="flex-1 py-1 px-2 rounded bg-rose-600/20 hover:bg-rose-600/40 text-rose-300 border border-rose-800/60 text-[10px] font-semibold transition"
                    >
                      + Spike Reading
                    </button>

                    <button
                      onClick={() =>
                        handleUpdate(sensor.id, sensor.normal_baseline)
                      }
                      disabled={isUpdating}
                      className="py-1 px-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[10px] transition"
                    >
                      Reset Baseline
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs text-slate-400">
          <span>
            Sensor spikes automatically boost report credibility and escalate incident priority.
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
