import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  // KPI
  getKPI: async () => {
    const res = await client.get("/kpi");
    return res.data;
  },

  // Incidents
  getIncidents: async (status = null, minPriority = null) => {
    const params = {};
    if (status) params.status = status;
    if (minPriority !== null) params.min_priority = minPriority;
    const res = await client.get("/incidents", { params });
    return res.data;
  },

  getIncidentDetail: async (id) => {
    const res = await client.get(`/incidents/${id}`);
    return res.data;
  },

  createIncident: async (payload) => {
    const res = await client.post("/incidents", payload);
    return res.data;
  },

  // Reports
  submitReport: async (payload) => {
    const res = await client.post("/reports", payload);
    return res.data;
  },

  // Roads & Junctions
  getJunctions: async () => {
    const res = await client.get("/junctions");
    return res.data;
  },

  getRoads: async () => {
    const res = await client.get("/roads");
    return res.data;
  },

  toggleRoad: async (roadId, isBlocked, blockageReason = "Hazard obstruction") => {
    const res = await client.post("/roads/toggle", {
      road_id: roadId,
      is_blocked: isBlocked,
      blockage_reason: blockageReason,
    });
    return res.data;
  },

  // Resources & Assignments
  getResources: async () => {
    const res = await client.get("/resources");
    return res.data;
  },

  getAssignments: async () => {
    const res = await client.get("/assignments");
    return res.data;
  },

  dispatchResource: async (incidentId, resourceId = null) => {
    const res = await client.post("/dispatch", {
      incident_id: incidentId,
      resource_id: resourceId,
    });
    return res.data;
  },

  approveAssignment: async (assignmentId) => {
    const res = await client.post(`/assignments/${assignmentId}/approve`);
    return res.data;
  },

  // Sensors
  getSensors: async () => {
    const res = await client.get("/sensors");
    return res.data;
  },

  updateSensor: async (sensorId, newValue) => {
    const res = await client.post(`/sensors/${sensorId}/update`, {
      new_value: newValue,
    });
    return res.data;
  },

  // Situation Report
  getSitRep: async () => {
    const res = await client.get("/sitrep");
    return res.data;
  },
};
