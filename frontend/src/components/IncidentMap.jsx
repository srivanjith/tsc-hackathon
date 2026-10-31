import React, { useEffect, useRef } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import L from "leaflet";

// Fix default leaflet icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Strategic National Hubs & Chennai Metro lookup
const PAN_INDIA_HUBS = {
  Delhi: { name: "Delhi National Logistics Command", lat: 28.6139, lng: 77.2090 },
  Mumbai: { name: "Mumbai Western Maritime Depot", lat: 19.0760, lng: 72.8777 },
  Kolkata: { name: "Kolkata Eastern Regional Hub", lat: 22.5726, lng: 88.3639 },
  Chennai: { name: "Chennai Southern Bay Command", lat: 13.0827, lng: 80.2707 },
  Guwahati: { name: "Guwahati Brahmaputra Command", lat: 26.1445, lng: 91.7362 },
  Kochi: { name: "Kochi Western Ghats Command", lat: 9.9312, lng: 76.2673 },
  Dehradun: { name: "Dehradun Himalayan Center", lat: 30.3165, lng: 78.0322 },
  Bhubaneswar: { name: "Bhubaneswar Cyclone Command", lat: 20.2961, lng: 85.8245 },
  Ahmedabad: { name: "Ahmedabad Western Depot", lat: 23.0225, lng: 72.5714 },
  Nagpur: { name: "Nagpur Central Strategic Spine", lat: 21.1458, lng: 79.0882 },
  Patna: { name: "Patna Ganga Basin Lifeline", lat: 25.5941, lng: 85.1376 },
  Srinagar: { name: "Srinagar Northern Mountain Base", lat: 34.0837, lng: 74.7973 },
  Bengaluru: { name: "Bengaluru Southern Plateau Depot", lat: 12.9716, lng: 77.5946 },
  Visakhapatnam: { name: "Visakhapatnam Naval Command", lat: 17.6868, lng: 83.2185 },
  // Local Chennai fallback nodes
  Central: { name: "Chennai Central HQ", lat: 13.0836, lng: 80.2754 },
  MountRoad: { name: "Mount Road", lat: 13.0600, lng: 80.2600 },
  Saidapet: { name: "Saidapet Bridge", lat: 13.0205, lng: 80.2230 },
  Guindy: { name: "Guindy Kathipara", lat: 13.0067, lng: 80.2030 },
  Velachery: { name: "Velachery Basin", lat: 12.9815, lng: 80.2180 },
  Adyar: { name: "Adyar Malar", lat: 13.0033, lng: 80.2550 },
  TNagar: { name: "T. Nagar", lat: 13.0418, lng: 80.2341 },
  Marina: { name: "Marina Coastal", lat: 13.0500, lng: 80.2824 },
  Tambaram: { name: "Tambaram GST", lat: 12.9249, lng: 80.1000 },
  Koyambedu: { name: "Koyambedu Hub", lat: 13.0694, lng: 80.1948 },
};

// Hazard emoji lookup
const getHazardIcon = (type = "") => {
  const t = type.toLowerCase();
  if (t.includes("cyclone")) return "🌀";
  if (t.includes("earthquake") || t.includes("seismic")) return "🌋";
  if (t.includes("landslide") || t.includes("debris")) return "🏔️";
  if (t.includes("fire")) return "🔥";
  return "🌊";
};

// Custom Multi-Hazard Incident Pin
const createIncidentPin = (incident) => {
  const isCritical = incident.priority_score >= 80 || incident.predicted_risk_level === "CRITICAL";
  const bgClass = isCritical ? "bg-[#DC3545]" : "bg-[#F59E0B]";
  const pulseClass = isCritical ? "pulse-critical" : "";
  const emoji = getHazardIcon(incident.type);

  const html = `
    <div class="relative flex items-center justify-center">
      <div class="w-9 h-9 rounded-full ${bgClass} border-2 border-white flex items-center justify-center text-white font-bold text-xs shadow-xl ${pulseClass}">
        <span class="mr-0.5 text-xs">${emoji}</span>
        <span class="text-[10px]">${Math.round(incident.priority_score)}</span>
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: "custom-incident-pin",
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
};

// Custom Strategic Resource Pin
const createResourcePin = (resource) => {
  let symbol = "🛡️";
  let bg = "bg-[#1677D2]";
  const t = (resource.type || "").toUpperCase();

  if (t.includes("BOAT") || t.includes("FLOTILLA")) {
    symbol = "🚤";
    bg = "bg-cyan-700";
  } else if (t.includes("AIRLIFT") || t.includes("IAF")) {
    symbol = "🚁";
    bg = "bg-indigo-700";
  } else if (t.includes("EARTHMOVER") || t.includes("HEAVY")) {
    symbol = "🚜";
    bg = "bg-amber-700";
  } else if (t.includes("NDRF")) {
    symbol = "🎖️";
    bg = "bg-emerald-700";
  }

  const html = `
    <div class="w-7 h-7 rounded-lg ${bg} border-2 border-white flex items-center justify-center text-xs shadow-md">
      <span>${symbol}</span>
    </div>
  `;

  return L.divIcon({
    html,
    className: "custom-resource-pin",
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  });
};

// Custom Evacuation Shelter Pin
const createShelterPin = () => {
  const html = `
    <div class="w-7 h-7 rounded-lg bg-emerald-600 border-2 border-white flex items-center justify-center text-white shadow-md">
      <span class="text-xs">🏕️</span>
    </div>
  `;
  return L.divIcon({
    html,
    className: "custom-shelter-pin",
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  });
};

function MapFlyTo({ selectedIncident }) {
  const map = useMap();
  useEffect(() => {
    if (selectedIncident && selectedIncident.latitude && selectedIncident.longitude) {
      map.flyTo([selectedIncident.latitude, selectedIncident.longitude], 9, {
        duration: 1.2,
      });
    }
  }, [selectedIncident, map]);
  return null;
}

export default function IncidentMap({
  incidents = [],
  roads = [],
  resources = [],
  shelters = [],
  assignments = [],
  selectedIncident,
  onSelectIncident,
}) {
  // Center of India overview
  const indiaCenter = [22.8, 80.5];

  return (
    <div className="w-full h-[540px] rounded-xl overflow-hidden border border-slate-200 shadow-sm relative bg-[#F5F8FC]">
      <MapContainer
        center={indiaCenter}
        zoom={5}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <MapFlyTo selectedIncident={selectedIncident} />

        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 1. National Transport Corridors & Arterial Highways */}
        {roads.map((road) => {
          const u = PAN_INDIA_HUBS[road.from_node];
          const v = PAN_INDIA_HUBS[road.to_node];
          if (!u || !v) return null;

          const positions = [
            [u.lat, u.lng],
            [v.lat, v.lng],
          ];

          return (
            <Polyline
              key={`road-${road.id}`}
              positions={positions}
              pathOptions={{
                color: road.blocked ? "#DC3545" : "#1677D2",
                weight: road.blocked ? 5 : 3.5,
                dashArray: road.blocked ? "8, 8" : undefined,
                opacity: road.blocked ? 0.95 : 0.65,
              }}
            >
              <Tooltip sticky>
                <div className="text-xs">
                  <div className="font-bold text-slate-800">
                    {road.road_name || `${road.from_node} ↔ ${road.to_node}`}
                  </div>
                  <div className="text-slate-500">
                    Highway: <strong>{road.highway_code || "NH"}</strong> • {road.distance_km} km
                  </div>
                  {road.blocked ? (
                    <div className="text-[#DC3545] font-bold mt-0.5">
                      ⛔ SEVERED / BLOCKED: {road.block_reason || "Landslide / Surge"}
                    </div>
                  ) : (
                    <div className="text-[#16A36A] font-semibold mt-0.5">
                      ✓ Open National Corridor
                    </div>
                  )}
                </div>
              </Tooltip>
            </Polyline>
          );
        })}

        {/* 2. Active Mission Routes (Original vs RippleGuard Detours) */}
        {assignments.map((assign) => {
          const isRerouted = !!assign.previous_route_json;
          const currNodes = assign.route_json || [];
          const prevNodes = assign.previous_route_json || [];

          const currCoords = currNodes
            .map((n) => PAN_INDIA_HUBS[n])
            .filter(Boolean)
            .map((d) => [d.lat, d.lng]);

          const prevCoords = prevNodes
            .map((n) => PAN_INDIA_HUBS[n])
            .filter(Boolean)
            .map((d) => [d.lat, d.lng]);

          return (
            <React.Fragment key={`assign-${assign.id}`}>
              {/* Previous severed path */}
              {isRerouted && prevCoords.length > 1 && (
                <Polyline
                  positions={prevCoords}
                  pathOptions={{
                    color: "#DC3545",
                    weight: 3.5,
                    dashArray: "6, 6",
                    opacity: 0.75,
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs text-[#DC3545]">
                      <strong>Previous Corridor (Severed by Disaster)</strong>
                    </div>
                  </Tooltip>
                </Polyline>
              )}

              {/* Current or Alternate Path */}
              {currCoords.length > 1 && (
                <Polyline
                  positions={currCoords}
                  pathOptions={{
                    color: isRerouted ? "#16A36A" : "#1677D2",
                    weight: isRerouted ? 5.5 : 4,
                    opacity: 0.95,
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs">
                      <strong className={isRerouted ? "text-[#16A36A]" : "text-[#1677D2]"}>
                        {isRerouted ? "⚡ RippleGuard National Detour" : "Direct National Deployment"}
                      </strong>
                      <div>{assign.resource_name} → {assign.incident_title}</div>
                    </div>
                  </Tooltip>
                </Polyline>
              )}
            </React.Fragment>
          );
        })}

        {/* 3. Strategic National Hub Nodes */}
        {Object.entries(PAN_INDIA_HUBS).map(([id, node]) => (
          <CircleMarker
            key={`hub-${id}`}
            center={[node.lat, node.lng]}
            radius={5}
            pathOptions={{
              color: "#1E293B",
              fillColor: "#FFFFFF",
              fillOpacity: 1,
              weight: 2.5,
            }}
          >
            <Tooltip direction="top" offset={[0, -6]}>
              <span className="text-[10px] font-bold text-slate-800">
                {node.name}
              </span>
            </Tooltip>
          </CircleMarker>
        ))}

        {/* 4. Shelters */}
        {shelters.map((shelter) => (
          <Marker
            key={`shelter-${shelter.id}`}
            position={[shelter.latitude, shelter.longitude]}
            icon={createShelterPin()}
          >
            <Popup>
              <div className="text-xs p-1 space-y-1">
                <div className="font-bold text-slate-800">{shelter.name}</div>
                <div className="text-slate-500 text-[11px]">{shelter.state} • {shelter.district}</div>
                <div className="text-slate-600">
                  Capacity: {shelter.capacity} | Occupancy: {shelter.occupancy}
                </div>
                <div className="text-[#16A36A] font-semibold">
                  Remaining Space: {shelter.capacity - shelter.occupancy} people
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 5. Strategic Defense & NDRF Resources */}
        {resources.map((resource) => (
          <Marker
            key={`res-${resource.id}`}
            position={[resource.latitude, resource.longitude]}
            icon={createResourcePin(resource)}
          >
            <Popup>
              <div className="text-xs p-1 space-y-1">
                <div className="font-bold text-slate-800">{resource.name}</div>
                <div className="text-slate-500 text-[11px]">{resource.state} • {resource.district}</div>
                <div className="text-slate-600">
                  Fleet Type: <strong>{resource.type}</strong>
                </div>
                <div className="text-[#1677D2] font-semibold">
                  Active Units: {resource.available_units} squadrons
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 6. Multi-Hazard Incidents */}
        {incidents.map((incident) => (
          <Marker
            key={`inc-${incident.id}`}
            position={[incident.latitude, incident.longitude]}
            icon={createIncidentPin(incident)}
          >
            <Popup>
              <div className="text-xs p-1 space-y-1.5 max-w-xs">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] px-1.5 py-0.5 rounded font-bold bg-red-100 text-[#DC3545]">
                    [SIMULATION]
                  </span>
                  <span className="font-bold text-slate-800 font-mono">
                    Priority: {Math.round(incident.priority_score)}/100
                  </span>
                </div>
                <div className="flex items-center gap-1.5 font-bold text-slate-900 leading-snug">
                  <span>{getHazardIcon(incident.type)}</span>
                  <span>{incident.title}</span>
                </div>
                <div className="text-slate-500 text-[11px]">
                  State: <strong>{incident.state}</strong> | Risk: <span className="font-bold text-rose-600">{incident.predicted_risk_level}</span>
                </div>
                <div className="text-slate-600 text-[11px]">
                  Sev: {incident.severity}/5 | Urg: {incident.urgency}/5 | Affected: ~{incident.affected_people}
                </div>
                <button
                  onClick={() => onSelectIncident && onSelectIncident(incident)}
                  className="w-full mt-1 py-1 rounded bg-[#1677D2] text-white font-semibold text-center hover:bg-blue-600 transition"
                >
                  View ML Explainability & Evidence
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Floating Legend */}
      <div className="absolute bottom-3 left-3 z-[1000] p-3 rounded-xl bg-white/95 backdrop-blur-sm border border-slate-200 shadow-md text-[11px] space-y-1">
        <div className="font-bold text-slate-800 mb-0.5">ResQAI Pan-India Grid</div>
        <div className="flex items-center gap-2">
          <span className="text-xs">🌊 🌀 🌋 🏔️ 🔥</span>
          <span className="text-slate-600">Multi-Hazard Incident Zones</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#DC3545]"></span>
          <span className="text-slate-600">Critical Priority (≥80)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 border-t-2 border-dashed border-[#DC3545]"></span>
          <span className="text-slate-600">Severed National Highway</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 bg-[#16A36A] rounded"></span>
          <span className="text-slate-600">Active RippleGuard Detour</span>
        </div>
      </div>
    </div>
  );
}
