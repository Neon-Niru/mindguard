const BASE = import.meta.env.VITE_API_URL || "/api";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${endpoint}`, {
    ...options,
    headers: { ...headers, ...options.headers },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const err = new Error(data.error || `Request failed (${res.status})`);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export const auth = {
  login: (email, password) =>
    request("/login", { method: "POST", body: { email, password } }),
  register: (full_name, email, password) =>
    request("/register", { method: "POST", body: { full_name, email, password } }),
  me: () => request("/me"),
  forgotPassword: (email) =>
    request("/forgot-password", { method: "POST", body: { email } }),
  resetPassword: (token, password) =>
    request("/reset-password", { method: "POST", body: { token, password } }),
};

export const dashboard = {
  get: () => request("/dashboard"),
};

export const planner = {
  list: () => request("/planner"),
  add: (task) => request("/planner", { method: "POST", body: task }),
  update: (taskId, updates) =>
    request(`/planner/${taskId}`, { method: "PUT", body: updates }),
  remove: (taskId) =>
    request(`/planner/${taskId}`, { method: "DELETE" }),
};

export const progress = {
  get: () => request("/progress"),
};

export const reportService = {
  get: () => request("/report"),
};

export const assessment = {
  get: (id) => request(`/assessment/${id}`),
};

export const settings = {
  get: () => request("/settings"),
  save: (data) => request("/settings", { method: "POST", body: data }),
};

export const interview = {
  send: (message, sessionId) =>
    request("/interview", { method: "POST", body: { message, session_id: sessionId } }),
};
