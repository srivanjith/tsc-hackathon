import React, { useState } from "react";
import {
  X,
  PlusCircle,
  ShieldAlert,
  ShieldCheck,
  Radio,
  Send,
  AlertTriangle,
} from "lucide-react";
import { api } from "../api";

const JUNCTION_OPTIONS = [
  { id: "J1", label: "J1 - Central Emergency HQ" },
  { id: "J2", label: "J2 - North Metro Rail Crossing" },
  { id: "J3", label: "J3 - Riverside North Causeway" },
  { id: "J4", label: "J4 - Hospital Sector & EMS Depot" },
  { id: "J5", label: "J5 - Commercial District Square" },
  { id: "J6", label: "J6 - East Valley Reservoir Gate" },
  { id: "J7", label: "J7 - Grand River Bridge South" },
  { id: "J8", label: "J8 - Civic Center & Relief Camp" },
  { id: "J9", label: "J9 - Industrial Canal Terminal" },
  { id: "J10", label: "J10 - South Bay Marina Dock" },
  { id: "J11", label: "J11 - West Highland Tunnel" },
  { id: "J12", label: "J12 - Low-lying Flood Colony" },
  { id: "J13", label: "J13 - University Campus Shelter" },
  { id: "J14", label: "J14 - Eastern Coastal Highway Toll" },
];

export default function ReportSubmissionModal({
  onClose,
  onSubmitSuccess,
  junctions = {},
}) {
  const [formData, setFormData] = useState({
    title: "",
    category: "Flood",
    severity: 4.0,
    affected_population: 150,
    vulnerability_factor: 1.3,
    nearest_junction: "J3",
    zone_name: "Riverside North",
    source_type: "VERIFIED_CITIZEN",
    author: "Citizen Alert Network",
    content: "Flash flood water rising to 1.5 meters near the junction. Several residents trapped.",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  // Live trust preview simulation
  const computePreviewTrust = () => {
    let base = 0.5;
    if (formData.source_type === "OFFICIAL_SENSOR") base = 0.95;
    else if (formData.source_type === "GOVT_AGENCY") base = 0.92;
    else if (formData.source_type === "VERIFIED_CITIZEN") base = 0.75;
    else if (formData.source_type === "SOCIAL_MEDIA") base = 0.45;
    else if (formData.source_type === "ANONYMOUS") base = 0.35;

    const lower = formData.content.toLowerCase();
    let flag = "Normal";

    if (
      lower.includes("prank") ||
      lower.includes("fake") ||
      lower.includes("alien") ||
      lower.includes("free cash") ||
      lower.includes("click link")
    ) {
      base = Math.max(0.1, base - 0.4);
      flag = "SPAM_HOAX Detected";
    } else if (
      lower.includes("meter") ||
      lower.includes("trapped") ||
      lower.includes("submerged") ||
      lower.includes("hospital")
    ) {
      base = Math.min(0.98, base + 0.1);
      flag = "Factual Detail Bonus";
    }

    return { trustPct: Math.round(base * 100), flag };
  };

  const preview = computePreviewTrust();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setError("Please provide an incident title");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const jNode = junctions[formData.nearest_junction] || {
        lat: 19.08,
        lng: 72.875,
      };

      const payload = {
        title: formData.title,
        description: formData.content,
        category: formData.category,
        severity: parseFloat(formData.severity),
        affected_population: parseInt(formData.affected_population, 10),
        vulnerability_factor: parseFloat(formData.vulnerability_factor),
        lat: jNode.lat,
        lng: jNode.lng,
        zone_name: formData.zone_name,
        nearest_junction: formData.nearest_junction,
        initial_report: {
          source_type: formData.source_type,
          author: formData.author,
          content: formData.content,
          lat: jNode.lat,
          lng: jNode.lng,
          zone_name: formData.zone_name,
        },
      };

      const created = await api.createIncident(payload);
      onSubmitSuccess && onSubmitSuccess(created);
      onClose();
    } catch (err) {
      console.error(err);
      setError("Failed to submit incident report. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl max-h-[90vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 uppercase">
                Multi-Source Ingestion
              </span>
            </div>
            <h2 className="text-base font-bold text-white mt-1">
              Submit Disaster Report / Evidence
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Ingest crowd-sourced, citizen, or sensor alerts evaluated by the Evidence Intelligence Agent.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 flex-1 overflow-y-auto text-xs">
          {error && (
            <div className="p-3 rounded-lg bg-rose-950 border border-rose-800 text-rose-200">
              {error}
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block font-semibold text-slate-300 mb-1">
              Incident Headline / Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Rapid Water Surge Submerging Residential Apartments"
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500"
            />
          </div>

          {/* Source Type and Author */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Source Type (Credibility Base)
              </label>
              <select
                value={formData.source_type}
                onChange={(e) =>
                  setFormData({ ...formData, source_type: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500"
              >
                <option value="OFFICIAL_SENSOR">Official IoT Sensor (95% Base)</option>
                <option value="GOVT_AGENCY">Government Agency (92% Base)</option>
                <option value="VERIFIED_CITIZEN">Verified Citizen (75% Base)</option>
                <option value="SOCIAL_MEDIA">Social Media / Twitter (45% Base)</option>
                <option value="ANONYMOUS">Anonymous Report (35% Base)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Author / Handle
              </label>
              <input
                type="text"
                value={formData.author}
                onChange={(e) =>
                  setFormData({ ...formData, author: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500"
              />
            </div>
          </div>

          {/* Category, Zone, Junction */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Disaster Type
              </label>
              <select
                value={formData.category}
                onChange={(e) =>
                  setFormData({ ...formData, category: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500"
              >
                <option value="Flood">Flood / Inundation</option>
                <option value="Earthquake">Earthquake / Seismic</option>
                <option value="Landslide">Landslide / Mudflow</option>
                <option value="Fire">Fire / Explosion</option>
                <option value="Structural">Structural Collapse</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Zone Name
              </label>
              <input
                type="text"
                value={formData.zone_name}
                onChange={(e) =>
                  setFormData({ ...formData, zone_name: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-300 mb-1">
                Nearest Junction Node
              </label>
              <select
                value={formData.nearest_junction}
                onChange={(e) =>
                  setFormData({ ...formData, nearest_junction: e.target.value })
                }
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500"
              >
                {JUNCTION_OPTIONS.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Sliders: Severity & Population */}
          <div className="grid grid-cols-2 gap-4 p-3 rounded-xl bg-slate-950 border border-slate-800">
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Severity Scale:</span>
                <strong className="text-rose-400 font-mono">
                  {formData.severity} / 5.0
                </strong>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={formData.severity}
                onChange={(e) =>
                  setFormData({ ...formData, severity: e.target.value })
                }
                className="w-full accent-rose-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Estimated At Risk:</span>
                <strong className="text-amber-400 font-mono">
                  ~{formData.affected_population} people
                </strong>
              </div>
              <input
                type="range"
                min="5"
                max="1000"
                step="5"
                value={formData.affected_population}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    affected_population: e.target.value,
                  })
                }
                className="w-full accent-amber-500"
              />
            </div>
          </div>

          {/* Report Content */}
          <div>
            <label className="block font-semibold text-slate-300 mb-1">
              Field Report Observation Content *
            </label>
            <textarea
              rows={3}
              required
              value={formData.content}
              onChange={(e) =>
                setFormData({ ...formData, content: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-rose-500 font-sans"
              placeholder="Describe what is seen (water depth, trapped people, debris)..."
            />
          </div>

          {/* Real-time Trust Preview Callout */}
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <div>
                <span className="font-semibold text-slate-300">
                  Pre-flight Trust Prediction:
                </span>
                <span className="text-slate-500 ml-1.5 font-mono">
                  ({preview.flag})
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`font-mono font-bold ${
                  preview.trustPct >= 70
                    ? "text-emerald-400"
                    : preview.trustPct >= 50
                    ? "text-amber-400"
                    : "text-purple-400"
                }`}
              >
                Estimated Trust: {preview.trustPct}%
              </span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                  preview.trustPct >= 50
                    ? "bg-emerald-950 text-emerald-400"
                    : "bg-purple-950 text-purple-400"
                }`}
              >
                {preview.trustPct >= 50 ? "Will Dispatch" : "Will Hold in Review"}
              </span>
            </div>
          </div>

          {/* Footer */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold shadow-lg shadow-rose-900/40 transition disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{isSubmitting ? "Evaluating..." : "Submit to Engine"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
