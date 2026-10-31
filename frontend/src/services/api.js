import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api",
  timeout: 15000,
});

export const getHealth = () => api.get("/health");
export const getDashboard = () => api.get("/dashboard");
export const getIncidents = (params) => api.get("/incidents", { params });
export const getIncidentMLExplanation = (id) => api.get(`/incidents/${id}/ml-explain`);
export const createIncident = (data) => api.post("/incidents", data);
export const submitEvidence = (data) => api.post("/evidence", data);
export const analyzeEvidence = (data) => api.post("/evidence/analyze", data);
export const getResources = () => api.get("/resources");
export const getShelters = () => api.get("/shelters");
export const getRoads = () => api.get("/roads");
export const getNationalHubs = () => api.get("/planning/hubs");
export const getAssignments = () => api.get("/assignments");
export const generatePlan = () => api.post("/planning/generate");
export const blockRoad = (roadId, reason = "Severe flood inundation and debris blockage") =>
  api.post(`/roads/${roadId}/block`, { reason });
export const unblockRoad = (roadId) => api.post(`/roads/${roadId}/unblock`);
export const replan = () => api.post("/planning/replan");
export const approveDecision = (decisionId) =>
  api.post(`/decisions/${decisionId}/approve`);
export const getDecisionLogs = () => api.get("/decisions");
export const getWeather = (city) => api.get("/weather", { params: { city } });
export const getAllHubsWeather = () => api.get("/weather/all");

// Live Real Data API Sync
export const syncLiveData = () => api.post("/data/sync-live");
export const getLiveSources = () => api.get("/data/live-sources");

export default api;
