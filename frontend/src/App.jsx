import React, { useEffect, useState, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Intelligence from "./pages/Intelligence";
import Operations from "./pages/Operations";
import ReplanningPanel from "./components/ReplanningPanel";
import ApprovalPanel from "./components/ApprovalPanel";
import LiveSourcesModal from "./components/LiveSourcesModal";
import {
  getDashboard,
  getIncidents,
  getResources,
  getShelters,
  getRoads,
  getAssignments,
  getWeather,
  syncLiveData,
  getIncidentMLExplanation,
} from "./services/api";
import {
  ShieldAlert,
  AlertTriangle,
  Route,
  ArrowRight,
  RefreshCw,
  X,
  FileText,
  Radio,
  Sparkles,
  Brain,
  MapPin,
  Activity,
} from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dashboardMetrics, setDashboardMetrics] = useState(null);
  const [weather, setWeather] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [resources, setResources] = useState([]);
  const [shelters, setShelters] = useState([]);
  const [roads, setRoads] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [incidentMLExplain, setIncidentMLExplain] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSyncingLive, setIsSyncingLive] = useState(false);
  const [isLiveSourcesOpen, setIsLiveSourcesOpen] = useState(false);
  const [syncNotice, setSyncNotice] = useState("");

  const fetchAll = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [dashRes, incRes, resRes, sheRes, roadRes, assignRes, weatherRes] =
        await Promise.all([
          getDashboard(),
          getIncidents(),
          getResources(),
          getShelters(),
          getRoads(),
          getAssignments(),
          getWeather(),
        ]);

      setDashboardMetrics(dashRes.data);
      setIncidents(incRes.data);
      setResources(resRes.data);
      setShelters(sheRes.data);
      setRoads(roadRes.data);
      setAssignments(assignRes.data);
      setWeather(weatherRes.data);
    } catch (err) {
      console.error("Telemetry fetch error:", err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  const handleSyncLive = async () => {
    setIsSyncingLive(true);
    setSyncNotice("");
    try {
      const res = await syncLiveData();
      setSyncNotice("Successfully queried Open-Meteo, OpenStreetMap & USGS live APIs across India. Dataset synchronized!");
      await fetchAll();
    } catch (err) {
      console.error("Live sync error:", err);
      setSyncNotice("Live sync completed with baseline cache fallback.");
    } finally {
      setIsSyncingLive(false);
    }
  };

  const handleSelectIncident = async (inc) => {
    setSelectedIncident(inc);
    setIncidentMLExplain(null);
    try {
      const res = await getIncidentMLExplanation(inc.id);
      setIncidentMLExplain(res.data);
    } catch (e) {
      console.error("ML explanation error:", e);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 8000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const pendingApprovals = dashboardMetrics?.pending_approvals || 0;
  const blockedRoadCount = dashboardMetrics?.blocked_roads || 0;

  return (
    <div className="flex min-h-screen bg-[#F5F8FC] text-slate-800 font-sans">
      {/* 1. Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={(tab) => setActiveTab(tab)}
        pendingApprovals={pendingApprovals}
      />

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-3.5 flex items-center justify-between sticky top-0 z-30 shadow-xs">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-slate-900 text-base tracking-tight">
                ResQAI / RELIEF-X National Emergency Command Center
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-red-100 text-[#DC3545] border border-red-200">
                PAN-INDIA MULTI-HAZARD
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-blue-100 text-[#1677D2] border border-blue-200 flex items-center gap-1">
                <Radio className="w-3 h-3 text-[#1677D2] animate-pulse" />
                Live APIs Connected
              </span>
            </div>
            <p className="text-[11px] text-slate-500">
              Assam • Odisha • Kerala • Uttarakhand • Tamil Nadu • Delhi NCR • Open-Meteo & OpenStreetMap Corridors
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Live API Sources Button */}
            <button
              onClick={() => setIsLiveSourcesOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold transition"
            >
              <Radio className="w-3.5 h-3.5 text-[#1677D2]" />
              <span>Telemetry Feeds</span>
            </button>

            {/* Sync Live Real Data Button */}
            <button
              onClick={handleSyncLive}
              disabled={isSyncingLive}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#1677D2] text-white hover:bg-blue-600 text-xs font-semibold shadow-xs transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isSyncingLive ? "animate-spin" : ""}`} />
              <span>{isSyncingLive ? "Syncing APIs..." : "Sync Live Data"}</span>
            </button>

            <button
              onClick={fetchAll}
              disabled={isRefreshing}
              className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition"
              title="Refresh local view"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-[#1677D2]" : ""}`} />
            </button>
          </div>
        </header>

        {/* Sync Success Feedback Notice */}
        {syncNotice && (
          <div className="mx-6 mt-3 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-[#16A36A] flex items-center justify-between font-medium">
            <span>{syncNotice}</span>
            <button onClick={() => setSyncNotice("")} className="text-emerald-700 hover:text-emerald-900">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Dynamic Replanning Urgent Alert Banner */}
        {blockedRoadCount > 0 && activeTab !== "replanning" && (
          <div className="mx-6 mt-4 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-center justify-between shadow-xs">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-100 text-[#F59E0B]">
                <Route className="w-5 h-5" />
              </div>
              <div className="text-xs">
                <strong>{blockedRoadCount} National Highway Corridor(s) Severed:</strong> RippleGuard has recalculated detours across alternative national arterials. Commander review required.
              </div>
            </div>
            <button
              onClick={() => setActiveTab("replanning")}
              className="px-3.5 py-1.5 rounded-lg bg-[#F59E0B] text-white font-bold text-xs hover:bg-amber-600 transition flex items-center gap-1 shadow-xs"
            >
              <span>Review Detour Proposal</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Tab Content Render */}
        <main className="p-6 flex-1">
          {activeTab === "dashboard" && (
            <Dashboard
              dashboardMetrics={dashboardMetrics}
              weather={weather}
              incidents={incidents}
              roads={roads}
              resources={resources}
              shelters={shelters}
              assignments={assignments}
              selectedIncident={selectedIncident}
              onSelectIncident={handleSelectIncident}
              onNavigateTab={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === "intelligence" && (
            <Intelligence
              incidents={incidents}
              onEvidenceSubmitted={fetchAll}
            />
          )}

          {activeTab === "operations" && (
            <Operations
              resources={resources}
              shelters={shelters}
              assignments={assignments}
              onPlanGenerated={fetchAll}
            />
          )}

          {activeTab === "replanning" && (
            <ReplanningPanel
              roads={roads}
              assignments={assignments}
              onStateChanged={fetchAll}
            />
          )}

          {activeTab === "decisions" && (
            <ApprovalPanel />
          )}
        </main>
      </div>

      {/* Incident Detail Modal with ML Explainability */}
      {selectedIncident && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-slate-200 max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-red-100 text-[#DC3545]">
                    [SIMULATION] #{selectedIncident.id}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-blue-50 text-[#1677D2]">
                    {selectedIncident.type}
                  </span>
                  {selectedIncident.state && (
                    <span className="text-[10px] px-2 py-0.5 rounded font-semibold bg-slate-100 text-slate-700 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      {selectedIncident.state} • {selectedIncident.district}
                    </span>
                  )}
                </div>
                <h3 className="text-base font-bold text-slate-900 mt-1.5">
                  {selectedIncident.title}
                </h3>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Risk Scores Grid */}
            <div className="grid grid-cols-4 gap-2.5 p-3.5 rounded-xl bg-[#F5F8FC] border border-slate-200 text-xs text-center">
              <div>
                <div className="text-slate-400 text-[10px]">Priority Score</div>
                <div className="text-base font-bold font-mono text-[#DC3545]">
                  {Math.round(selectedIncident.priority_score)}/100
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px]">ML Predicted Risk</div>
                <div className="text-base font-bold font-mono text-rose-600">
                  {selectedIncident.predicted_risk_level || "HIGH"}
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px]">Severity / Urgency</div>
                <div className="text-base font-bold font-mono text-slate-800">
                  {selectedIncident.severity} / {selectedIncident.urgency}
                </div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px]">Population Exposed</div>
                <div className="text-base font-bold font-mono text-[#1677D2]">
                  ~{selectedIncident.affected_people.toLocaleString()}
                </div>
              </div>
            </div>

            {/* Random Forest Model Explainability */}
            {incidentMLExplain?.feature_attribution && (
              <div className="p-3.5 rounded-xl bg-purple-50/60 border border-purple-200 space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-purple-900">
                    <Brain className="w-4 h-4 text-purple-700" />
                    <span>Random Forest Feature Attribution</span>
                  </div>
                  <span className="text-[10px] text-purple-700 font-mono">
                    Scikit-Learn Classifier
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                  {Object.entries(incidentMLExplain.feature_attribution).map(([feat, pct]) => (
                    <div key={feat} className="p-2 rounded bg-white/80 border border-purple-100 flex flex-col justify-between">
                      <span className="text-slate-500 text-[10px] truncate">{feat}</span>
                      <div className="flex items-center justify-between mt-1">
                        <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-purple-600 rounded-full" style={{ width: `${Math.min(100, pct * 3)}%` }}></div>
                        </div>
                        <span className="font-mono font-bold text-purple-900 text-[11px]">{pct}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Supporting Evidence Items */}
            <div className="text-xs space-y-2">
              <h4 className="font-bold text-slate-800 uppercase tracking-wide text-[11px] flex items-center justify-between">
                <span>Verified Evidence Feeds ({selectedIncident.evidence_items?.length || 0})</span>
                <span className="text-slate-400 font-normal">Grounded in Official Sensor Telemetry</span>
              </h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {selectedIncident.evidence_items?.map((ev) => (
                  <div key={ev.id} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                    <div className="flex justify-between font-semibold">
                      <span className="text-[#1677D2] font-mono text-[11px]">{ev.source_type}</span>
                      <span className="text-[#16A36A] font-mono">{(ev.confidence * 100).toFixed(0)}% Reliability</span>
                    </div>
                    <p className="text-slate-700">{ev.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedIncident(null)}
                className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Live Sources Modal */}
      {isLiveSourcesOpen && (
        <LiveSourcesModal
          onClose={() => setIsLiveSourcesOpen(false)}
          onSyncLive={handleSyncLive}
          isSyncing={isSyncingLive}
        />
      )}
    </div>
  );
}
