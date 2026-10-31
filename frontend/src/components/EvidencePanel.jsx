import React, { useState } from "react";
import {
  Brain,
  ShieldCheck,
  AlertCircle,
  Copy,
  Sparkles,
  Send,
  Radio,
  FileText,
  CheckCircle,
  Hash,
} from "lucide-react";
import { analyzeEvidence, submitEvidence } from "../services/api";

const SOURCE_OPTIONS = [
  { id: "ISRO_BHUVAN", label: "ISRO Bhuvan Satellite Imagery (0.96 Base)" },
  { id: "IMD_WEATHER", label: "IMD Doppler Radar Alert (0.95 Base)" },
  { id: "CWC_GAUGE", label: "CWC River Discharge Level (0.94 Base)" },
  { id: "NDEM_ALERT", label: "NDEM National Hazard Alert (0.95 Base)" },
  { id: "GOVERNMENT", label: "State Disaster Authority (SDMA) (0.92 Base)" },
  { id: "FIELD", label: "NDRF / SDRF Field Command (0.90 Base)" },
  { id: "HOSPITAL", label: "District Medical Center (0.90 Base)" },
  { id: "CITIZEN", label: "Citizen Distress Dispatch (0.55 Base)" },
  { id: "UNVERIFIED", label: "Unverified Social Stream (0.30 Base)" },
];

export default function EvidencePanel({ onEvidenceSubmitted, incidents = [] }) {
  const [rawText, setRawText] = useState(
    "Guwahati Brahmaputra river embankment breached near Pandu port. Flood water depth exceeds 2.1 meters. 300+ villagers cut off on chars requiring NDRF shallow rescue crafts."
  );
  const [sourceType, setSourceType] = useState("ISRO_BHUVAN");
  const [selectedIncidentId, setSelectedIncidentId] = useState(incidents[0]?.id || "");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState("");

  const handleAnalyze = async () => {
    if (!rawText.trim()) return;
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setSubmitMessage("");
    try {
      const res = await analyzeEvidence({
        raw_text: rawText,
        source_type: sourceType,
      });
      setAnalysisResult(res.data);
    } catch (err) {
      console.error("AI Analysis error:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    if (!rawText.trim()) return;
    setIsSubmitting(true);
    try {
      await submitEvidence({
        incident_id: selectedIncidentId ? parseInt(selectedIncidentId, 10) : null,
        source_type: sourceType,
        description: rawText,
        verified: ["ISRO_BHUVAN", "IMD_WEATHER", "CWC_GAUGE", "NDEM_ALERT", "GOVERNMENT", "FIELD", "HOSPITAL"].includes(sourceType),
      });
      setSubmitMessage("Report corroborated and verified in Pan-India evidence registry!");
      onEvidenceSubmitted && onEvidenceSubmitted();
    } catch (err) {
      console.error("Submission error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-1">
          <Brain className="w-5 h-5 text-[#1677D2]" />
          <h2 className="text-base font-bold text-slate-800">
            Multi-Hazard Evidence Intelligence & Corroboration Engine
          </h2>
        </div>
        <p className="text-xs text-slate-500">
          Evaluates multi-source emergency reports using weighted source reliability (ISRO Bhuvan, IMD, CWC, NDEM), TF-IDF vector text similarity for duplicate/rumor detection, and Groq LLaMA-3 factual extraction.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Report Ingestion Form */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700">
            Ingest Emergency Report / Sensor Alert
          </h3>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Source Classification & Verification Tier
            </label>
            <select
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="w-full text-xs p-2.5 rounded-lg border border-slate-200 bg-[#F5F8FC] focus:outline-none focus:border-[#1677D2]"
            >
              {SOURCE_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Link to Existing Incident (Optional)
            </label>
            <select
              value={selectedIncidentId}
              onChange={(e) => setSelectedIncidentId(e.target.value)}
              className="w-full text-xs p-2.5 rounded-lg border border-slate-200 bg-[#F5F8FC] focus:outline-none focus:border-[#1677D2]"
            >
              <option value="">-- General Unlinked Disaster Report --</option>
              {incidents.map((inc) => (
                <option key={inc.id} value={inc.id}>
                  #{inc.id} [{inc.state}] - {inc.title.slice(0, 45)}...
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">
              Distress Text, Satellite Observation, or Field Dispatch
            </label>
            <textarea
              rows={4}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full text-xs p-3 rounded-lg border border-slate-200 bg-[#F5F8FC] focus:outline-none focus:border-[#1677D2] font-sans"
              placeholder="Enter distress message, satellite anomaly notes, or field report..."
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-[#1677D2] text-white text-xs font-semibold hover:bg-blue-600 transition shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isAnalyzing ? "Analyzing NLP & Corroboration..." : "Analyze with Groq & TF-IDF"}</span>
            </button>

            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="py-2 px-4 rounded-lg bg-[#16A36A] text-white text-xs font-semibold hover:bg-emerald-600 transition shadow-sm disabled:opacity-50 flex items-center gap-1.5"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Commit Evidence</span>
            </button>
          </div>

          {submitMessage && (
            <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-[#16A36A] flex items-center gap-2 font-medium">
              <CheckCircle className="w-4 h-4" />
              <span>{submitMessage}</span>
            </div>
          )}
        </div>

        {/* Right: AI Extraction & Reliability Output */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700">
            NLP Verification & Corroboration Telemetry
          </h3>

          {analysisResult ? (
            <div className="space-y-3.5 text-xs">
              {/* Reliability & TF-IDF Card */}
              <div className="p-3.5 rounded-xl bg-[#F5F8FC] border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="text-slate-500 text-[11px]">
                    Adjusted Evidence Reliability
                  </div>
                  <div className="text-2xl font-bold font-mono text-[#1677D2]">
                    {(analysisResult.reliability_score * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                      analysisResult.reliability_score >= 0.8
                        ? "bg-emerald-100 text-[#16A36A]"
                        : analysisResult.reliability_score >= 0.5
                        ? "bg-amber-100 text-[#F59E0B]"
                        : "bg-red-100 text-[#DC3545]"
                    }`}
                  >
                    Confidence: {analysisResult.confidence_level}
                  </span>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {analysisResult.is_duplicate ? (
                      <span className="text-[#DC3545] font-semibold flex items-center gap-1 justify-end">
                        <Copy className="w-3 h-3" /> Duplicate Detected (TF-IDF Similarity: {analysisResult.tfidf_analysis?.highest_similarity})
                      </span>
                    ) : (
                      <span className="text-[#16A36A] font-semibold">
                        Unique Stream ({analysisResult.corroboration_count || 0} Corroborating Signals)
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* TF-IDF Engine Badges */}
              {analysisResult.nlp_flags && analysisResult.nlp_flags.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] text-slate-400 font-medium">NLP Flags:</span>
                  {analysisResult.nlp_flags.map((flag, i) => (
                    <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-[#1677D2] border border-blue-200">
                      {flag}
                    </span>
                  ))}
                </div>
              )}

              {/* Extracted Structured JSON */}
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto max-h-56">
                <pre>{JSON.stringify(analysisResult.extracted_data, null, 2)}</pre>
              </div>

              {/* Contradictions & Missing Info */}
              {analysisResult.extracted_data?.possible_contradictions && (
                <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-[#F59E0B] text-[11px] flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{analysisResult.extracted_data.possible_contradictions}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center border-2 border-dashed border-slate-200 rounded-xl text-xs text-slate-400 space-y-2">
              <Sparkles className="w-6 h-6 text-slate-300 mx-auto" />
              <p>
                Click <strong>"Analyze with Groq & TF-IDF"</strong> to extract entities, test cosine similarity against known disaster reports, and compute Bayesian credibility.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
