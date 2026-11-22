
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000,
});

export const getNetworkSummary = async () => {
  const response = await API.get("/api/network/summary");
  return response.data;
};

export const getTopNodes = async (
  sortBy = "betweenness",
  limit = 10
) => {
  const response = await API.get("/api/network/top-nodes", {
    params: {
      sort_by: sortBy,
      limit,
    },
  });

  return response.data;
};

export const getNodeDetails = async (nodeId) => {
  const response = await API.get(`/api/network/nodes/${nodeId}`);
  return response.data;
};

export const simulateDisruption = async (nodeId) => {
  const response = await API.post(
    `/api/network/simulate/${nodeId}`
  );

  return response.data;
};


export const getNodeNeighbors = async (nodeId) => {
  const response = await API.get(
    `/api/network/nodes/${nodeId}/neighbors`
  );

  return response.data;
};


export const checkBackendHealth = async () => {
  const response = await API.get("/health");
  return response.data;
};
