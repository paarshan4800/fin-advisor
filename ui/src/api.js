import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:5001/api",
  headers: {
    "Content-Type": "application/json",
  },
});

const api = {
  get: (url, params = {}, config = {}) =>
    apiClient.get(url, { params, ...config }),

  post: (url, data = {}, config = {}) =>
    apiClient.post(url, data, config),
};

export default api;
