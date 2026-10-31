import React, { useState, useEffect } from "react";
import StatCard from "../components/StatCard";
import IncidentMap from "../components/IncidentMap";
import IncidentList from "../components/IncidentList";
import {
  AlertTriangle,
  ShieldAlert,
  LifeBuoy,
  Home,
  Route,
  Users,
  CloudRain,
  Wind,
  Thermometer,
  Compass,
  Radio,
  MapPin,
  Layers,
} from "lucide-react";
import { getAllHubsWeather } from "../services/api";

const HAZARD_TYPES = [
  { id: "ALL", label: "All Multi-Hazards", icon: "🌐" },
  { id: "Flood", label: "Floods & Surge", icon: "🌊" },
  { id: "Cyclone", label: "Cyclones & Gale", icon: "🌀" },
  { id: "Earthquake", label: "Earthquakes", icon: "🌋" },
  { id: "Landslide", label: "Landslides & Debris", icon: "🏔️" },
  { id: "Forest Fire", label: "Forest Fires", icon: "🔥" },
];

export default function Dashboard({
  dashboardMetrics,
  weather,
  incidents = [],
  roads = [],
  resources = [],
  shelters = [],
  assignments = [],
  selectedIncident,
  onSelectIncident,
  onNavigateTab,
}) {
  const [selectedHazard, setSelectedHazard] = useState("ALL");
  const [selectedRegion, setSelectedRegion] = useState("ALL");
  const [hubsWeather, setHubsWeather] = useState([]);

  useEffect(() => {
    getAllHubsWeather()
      .then((res) => {
        if (Array.isArray(res.data)) {
          setHubsWeather(res.data);
        }
      })
      .catch((e) => console.log("Hubs weather load:", e));
  }, []);

  // Filter incidents based on selected hazard & state
  const filteredIncidents = incidents.filter((inc) => {
    const matchesHazard =
      selectedHazard === "ALL" ||
      inc.type.toLowerCase().includes(selectedHazard.toLowerCase());
    const matchesRegion =
      selectedRegion === "ALL" ||
      (inc.state && inc.state.toLowerCase().includes(selectedRegion.toLowerCase()));
    return matchesHazard && matchesRegion;
  });

  return (
    <div className="space-y-6">
      {/* 1. Pan-India Multi-Hub Weather & Disaster Telemetry Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-[#1677D2] animate-pulse" />
            <h3 className="font-bold text-xs uppercase tracking-wide text-slate-800">
              Live Regional Weather Feeds (Open-Meteo & IMD Telemetry)
            </h3>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            Direct Sat-Feed & Radar Observation
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {(hubsWeather.length > 0
            ? hubsWeather
            : [
                { city: "Guwahati, Assam", temperature_c: 24.2, precipitation_mm: 32.5, wind_speed_kmh: 28.0, risk_level: "RED ALERT" },
                { city: "Bhubaneswar, Odisha", temperature_c: 28.1, precipitation_mm: 45.0, wind_speed_kmh: 75.0, risk_level: "RED ALERT" },
                { city: "Dehradun, UK", temperature_c: 19.5, precipitation_mm: 18.2, wind_speed_kmh: 22.0, risk_level: "ORANGE" },
                { city: "Kochi, Kerala", temperature_c: 27.0, precipitation_mm: 22.0, wind_speed_kmh: 30.0, risk_level: "ORANGE" },
                { city: "Mumbai, MH", temperature_c: 29.5, precipitation_mm: 8.5, wind_speed_kmh: 24.0, risk_level: "MODERATE" },
                { city: "New Delhi, NCR", temperature_c: 26.0, precipitation_mm: 0.0, wind_speed_kmh: 14.0, risk_level: "WATCH" },
                { city: "Chennai, TN", temperature_c: 28.5, precipitation_mm: 24.5, wind_speed_kmh: 34.0, risk_level: "RED ALERT" },
              ]
          ).map((hub, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-[#F5F8FC] border border-slate-200/80 flex flex-col justify-between text-xs space-y-1"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800 text-[11px] truncate">
                  {hub.city.split(",")[0]}
                </span>
                <span
                  className={`text-[9px] font-bold px-1 py-0.2 rounded ${
                    hub.risk_level?.includes("RED")
                      ? "bg-red-100 text-[#DC3545]"
                      : hub.risk_level?.includes("ORANGE")
                      ? "bg-amber-100 text-[#F59E0B]"
                      : "bg-slate-200 text-slate-700"
                  }`}
                >
                  {hub.risk_level?.split("/")[0] || "LIVE"}
                </span>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                <span>{hub.temperature_c}°C</span>
                <span className="text-[#1677D2] font-semibold">{hub.precipitation_mm}mm</span>
                <span>{hub.wind_speed_kmh}km/h</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Top Metric Cards */}
      {dashboardMetrics && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatCard
            label="Active Incidents"
            value={dashboardMetrics.active_incidents}
            subtext="Pan-India Emergency Zones"
            icon={AlertTriangle}
            variant="blue"
          />
          <StatCard
            label="Critical Threats"
            value={dashboardMetrics.critical_incidents}
            subtext="ML Predicted Level: CRITICAL"
            icon={ShieldAlert}
            variant="red"
            badge="P0 Priority"
          />
          <StatCard
            label="Active Units"
            value={dashboardMetrics.available_resources}
            subtext="NDRF, IAF, Coast Guard"
            icon={LifeBuoy}
            variant="green"
            onClick={() => onNavigateTab && onNavigateTab("operations")}
          />
          <StatCard
            label="Shelter Space"
            value={dashboardMetrics.shelter_remaining_capacity}
            subtext={`Occupied: ${dashboardMetrics.shelter_occupancy}`}
            icon={Home}
            variant="slate"
            onClick={() => onNavigateTab && onNavigateTab("operations")}
          />
          <StatCard
            label="Blocked Corridors"
            value={dashboardMetrics.blocked_roads}
            subtext="National Arterials Severed"
            icon={Route}
            variant={dashboardMetrics.blocked_roads > 0 ? "red" : "slate"}
            badge={dashboardMetrics.blocked_roads > 0 ? "Rerouting" : "Clear"}
            onClick={() => onNavigateTab && onNavigateTab("replanning")}
          />
          <StatCard
            label="Unmet Demand"
            value={dashboardMetrics.unmet_demand_people}
            subtext="Residents requiring evacuation"
            icon={Users}
            variant={dashboardMetrics.unmet_demand_people > 0 ? "amber" : "slate"}
          />
        </div>
      )}

      {/* 3. Hazard Class Filter Pills */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          {HAZARD_TYPES.map((h) => (
            <button
              key={h.id}
              onClick={() => setSelectedHazard(h.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                selectedHazard === h.id
                  ? "bg-[#1677D2] text-white shadow-sm"
                  : "bg-white text-slate-700 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              <span>{h.icon}</span>
              <span>{h.label}</span>
            </button>
          ))}
        </div>

        {/* Regional Quick Filters */}
        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-slate-400 text-[11px] font-medium flex items-center gap-1">
            <MapPin className="w-3 h-3 text-slate-400" /> State:
          </span>
          {["ALL", "Assam", "Odisha", "Kerala", "Uttarakhand", "Tamil Nadu"].map((st) => (
            <button
              key={st}
              onClick={() => setSelectedRegion(st)}
              className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                selectedRegion === st
                  ? "bg-slate-800 text-white font-bold"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* 4. Split Screen: Map (7 cols) + Prioritized Queue (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-7">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Pan-India Spatial Coordination Grid (National Corridors)</span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">
              NH44 • NH48 • NH16 • NH27
            </span>
          </div>

          <IncidentMap
            incidents={filteredIncidents}
            roads={roads}
            resources={resources}
            shelters={shelters}
            assignments={assignments}
            selectedIncident={selectedIncident}
            onSelectIncident={onSelectIncident}
          />
        </div>

        <div className="lg:col-span-5">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-xs uppercase tracking-wide text-slate-700">
              Ranked Multi-Hazard Queue ({filteredIncidents.length})
            </h3>
            <span className="text-[11px] text-slate-400">
              Scored by ML & Urgency
            </span>
          </div>

          <IncidentList
            incidents={filteredIncidents}
            selectedIncident={selectedIncident}
            onSelectIncident={onSelectIncident}
          />
        </div>
      </div>
    </div>
  );
}
