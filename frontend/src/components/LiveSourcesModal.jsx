import React, { useEffect, useState } from "react";
import {
  X,
  Radio,
  CloudRain,
  MapPin,
  Activity,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";
import { getLiveSources } from "../services/api";

export default function LiveSourcesModal({ onClose, onSyncLive, isSyncing }) {
  const [sourcesData, setSourcesData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLiveSources()
      .then((res) => {
        setSourcesData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl border border-slate-200 max-w-2xl w-full p-6 shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <h2 className="text-base font-bold text-slate-900">
                Connected Real-World APIs & Telemetry Feeds
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              RELIEF-X is actively integrated with live open data APIs for meteorological, geospatial, and hazard telemetry.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="py-4 flex-1 overflow-y-auto space-y-3.5 text-xs">
          {loading ? (
            <div className="text-center py-10 text-slate-400">
              Querying live API endpoints...
            </div>
          ) : (
            sourcesData?.sources.map((src, i) => (
              <div
                key={i}
                className="p-3.5 rounded-xl border border-slate-200 bg-[#F5F8FC] space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Radio className="w-4 h-4 text-[#1677D2]" />
                    <span className="font-bold text-slate-900">{src.name}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-[#16A36A]">
                    {src.status}
                  </span>
                </div>

                <div className="text-[11px] text-slate-500 space-y-0.5">
                  <div>
                    <strong>Endpoint:</strong>{" "}
                    <code className="text-slate-700 bg-white px-1.5 py-0.2 rounded border border-slate-200">
                      {src.endpoint}
                    </code>
                  </div>
                  <div>
                    <strong>Target:</strong> {src.target}
                  </div>
                </div>

                {src.latest_telemetry && (
                  <div className="p-2 rounded bg-white border border-slate-200 grid grid-cols-3 gap-2 text-[11px] text-center">
                    <div>
                      <span className="text-slate-400">Live Temp:</span>{" "}
                      <strong>{src.latest_telemetry.temperature}°C</strong>
                    </div>
                    <div>
                      <span className="text-slate-400">Rain Gauge:</span>{" "}
                      <strong className="text-[#1677D2]">{src.latest_telemetry.precipitation} mm</strong>
                    </div>
                    <div>
                      <span className="text-slate-400">Wind:</span>{" "}
                      <strong>{src.latest_telemetry.wind_speed} km/h</strong>
                    </div>
                  </div>
                )}

                {src.sample_events && (
                  <div className="p-2 rounded bg-white border border-slate-200 text-[10px] space-y-1">
                    <span className="font-semibold text-slate-500">Live Global Hazard Samples:</span>
                    {src.sample_events.map((ev, eIdx) => (
                      <div key={eIdx} className="text-slate-700 truncate">
                        • {ev.title} ({ev.place})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={onSyncLive}
            disabled={isSyncing}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#1677D2] text-white text-xs font-semibold hover:bg-blue-600 transition shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? "animate-spin" : ""}`} />
            <span>{isSyncing ? "Fetching from APIs..." : "Fetch & Sync Real Dataset Now"}</span>
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
