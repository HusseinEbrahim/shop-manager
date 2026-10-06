const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function apiRequest(path, { method = "GET", body, responseType } = {}) {
  const token = localStorage.getItem("token");
  const isForm = body instanceof URLSearchParams;

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      ...(body && !isForm ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && path !== "/auth/login") {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Session expired");
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : "Something went wrong");
  }

  if (res.status === 204) return null;
  if (responseType === "blob") return res.blob();
  return res.json();
}