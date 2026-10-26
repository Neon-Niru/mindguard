const BASE = (import.meta.env.VITE_API_URL || "/api").replace(/\/+$/, "");

const AUTH_ERRORS = new Set([
  "Authorization required",
  "Token expired",
  "Invalid token",
  "Session expired. Please log in again.",
  "Account no longer exists",
]);

function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.dispatchEvent(new Event("mindguard:unauthorized"));
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { Accept: "application/json" };

  if (token) headers.Authorization = `Bearer ${token}`;

  const hasBody = options.body !== undefined && options.body !== null;
  if (hasBody) headers["Content-Type"] = "application/json";

  let res;
  try {
    res = await fetch(`${BASE}${endpoint}`, {
      ...options,
      headers: { ...headers, ...options.headers },
      body: hasBody ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    const err = new Error(
      "Unable to reach the MindGuard server. Please check your connection and try again."
    );
    err.status = 0;
    throw err;
  }

  const text = await res.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = {};
    }
  }

  if (!res.ok) {
    const message = data.error || `Request failed (${res.status})`;

    if (res.status === 401 && token && AUTH_ERRORS.has(data.error)) {
      clearSession();
    }

    const err = new Error(message);
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
  updateProfile: (updates) =>
    request("/me", { method: "PUT", body: updates }),
  changePassword: (current_password, new_password) =>
    request("/change-password", {
      method: "POST",
      body: { current_password, new_password },
    }),
  exportData: () => request("/me/export"),
  deleteAccount: (password) =>
    request("/me", { method: "DELETE", body: { password } }),
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
    request("/interview", {
      method: "POST",
      body: { message, session_id: sessionId || undefined },
    }),
};
