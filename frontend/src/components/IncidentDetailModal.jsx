import React, { useEffect, useState } from "react";
import {
  X,
  ShieldCheck,
  ShieldAlert,
  Calculator,
  Brain,
  FileText,
  Send,
  AlertTriangle,
  Radio,
  CheckCircle2,
} from "lucide-react";
import { api } from "../api";

export default function IncidentDetailModal({
  incident,
  onClose,
  onDispatchClick,
}) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!incident) return;
    setLoading(true);
    api
      .getIncidentDetail(incident.id)
      .then((data) => {
        setDetail(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch incident detail", err);
        setLoading(false);
      });
  }, [incident]);

  if (!incident) return null;

  const breakdown = detail?.breakdown;
  const reports = detail?.reports || [];
  const trustPct = Math.round(incident.credibility_score * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950/50 sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs px-2 py-0.5 rounded font-bold bg-slate-800 text-slate-300 uppercase">
                {incident.category}
              </span>
              <span className="text-xs text-slate-400">
                {incident.zone_name} • Node {incident.nearest_junction}
              </span>
              <span
                className={`text-xs px-2 py-0.5 rounded font-bold ${
                  incident.rescue_priority_score >= 75
                    ? "bg-rose-950 text-rose-300 border border-rose-800"
                    : incident.credibility_score < 0.5
                    ? "bg-purple-950 text-purple-300 border border-purple-800"
                    : "bg-amber-950 text-amber-300 border border-amber-800"
                }`}
              >
                Score: {Math.round(incident.rescue_priority_score)}/100
              </span>
            </div>
            <h2 className="text-lg font-bold text-white leading-tight">
              {incident.title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          {/* 1. Mathematical Breakdown Card (Jury Transparent) */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-slate-200">
                <Calculator className="w-4 h-4 text-rose-400" />
                <span>Explainable Priority Formula Breakdown</span>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                Rescue Priority = Base Urgency × Credibility
              </span>
            </div>

            {breakdown ? (
              <div className="space-y-3 text-xs">
                {/* Visual Math Formula */}
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80 font-mono text-center text-slate-300">
                  <span className="text-rose-400">
                    ({breakdown.severity_weight} × {breakdown.severity_normalized}
                    )
                  </span>{" "}
                  +{" "}
                  <span className="text-amber-400">
                    ({breakdown.population_weight} ×{" "}
                    {breakdown.population_normalized})
                  </span>{" "}
                  +{" "}
                  <span className="text-cyan-400">
                    ({breakdown.vulnerability_weight} ×{" "}
                    {breakdown.vulnerability_normalized})
                  </span>{" "}
                  ={" "}
                  <strong className="text-white">
                    {breakdown.base_urgency} Base
                  </strong>
                  <div className="mt-1 text-slate-400">
                    {breakdown.base_urgency} ×{" "}
                    <span className="text-emerald-400 font-bold">
                      {breakdown.credibility_multiplier} Trust
                    </span>{" "}
                    ={" "}
                    <strong className="text-rose-400 text-sm">
                      {breakdown.rescue_priority_score} Final Priority
                    </strong>
                  </div>
                </div>

                {/* Progress Bars */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Severity (45%)</span>
                      <strong className="text-slate-200">
                        {breakdown.severity_value}/5.0
                      </strong>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-rose-500 rounded-full"
                        style={{ width: `${breakdown.severity_normalized}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Population (35%)</span>
                      <strong className="text-slate-200">
                        ~{breakdown.population_value} people
                      </strong>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-amber-500 rounded-full"
                        style={{ width: `${breakdown.population_normalized}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Trust Multiplier</span>
                      <strong
                        className={
                          trustPct >= 70
                            ? "text-emerald-400"
                            : trustPct >= 50
                            ? "text-amber-400"
                            : "text-purple-400"
                        }
                      >
                        {trustPct}%
                      </strong>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          trustPct >= 70
                            ? "bg-emerald-500"
                            : trustPct >= 50
                            ? "bg-amber-500"
                            : "bg-purple-500"
                        }`}
                        style={{ width: `${trustPct}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-500">Loading formula breakdown...</div>
            )}
          </div>

          {/* 2. AI Reasoning / Explainability Section */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 font-bold text-sm text-slate-200">
              <Brain className="w-4 h-4 text-purple-400" />
              <span>AI Situation Assessment & Justification</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              {incident.reasoning || "Analyzing situational telemetry..."}
            </p>
          </div>

          {/* 3. Associated Evidence Reports (Credibility Engine) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-slate-200">
                <FileText className="w-4 h-4 text-cyan-400" />
                <span>Evidence Reports & Source Trust ({reports.length})</span>
              </div>
              <span className="text-xs text-slate-400">
                Evaluated by Evidence Intelligence Agent
              </span>
            </div>

            <div className="space-y-2">
              {reports.map((rep) => {
                const credPct = Math.round(rep.final_report_credibility * 100);
                return (
                  <div
                    key={rep.id}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-200">
                          {rep.author}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-400">
                          {rep.source_type}
                        </span>
                      </div>
                      <span
                        className={`font-mono font-bold text-xs ${
                          credPct >= 70
                            ? "text-emerald-400"
                            : credPct >= 50
                            ? "text-amber-400"
                            : "text-purple-400"
                        }`}
                      >
                        Trust: {credPct}%
                      </span>
                    </div>

                    <p className="text-slate-300">{rep.content}</p>

                    <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
                      <span>NLP Flag: <strong className="text-slate-300">{rep.nlp_flags}</strong></span>
                      {rep.sensor_correlation_note && (
                        <span className="text-cyan-400 flex items-center gap-1">
                          <Radio className="w-3 h-3" />
                          {rep.sensor_correlation_note}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-end gap-3 sticky bottom-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
          >
            Close
          </button>
          <button
            onClick={() => {
              onClose();
              onDispatchClick(incident);
            }}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-900/30 transition"
          >
            <Send className="w-4 h-4" />
            <span>Dispatch Rescue Team</span>
          </button>
        </div>
      </div>
    </div>
  );
}
