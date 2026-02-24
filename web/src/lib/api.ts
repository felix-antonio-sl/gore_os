const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") localStorage.setItem("goreos_token", token);
  }

  getToken(): string | null {
    if (!this.token && typeof window !== "undefined") {
      this.token = localStorage.getItem("goreos_token");
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") localStorage.removeItem("goreos_token");
  }

  async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { ...headers, ...options?.headers },
    });

    if (res.status === 401) {
      this.clearToken();
      if (typeof window !== "undefined") window.location.href = "/login";
      throw new Error("No autorizado");
    }
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `Error ${res.status}`);
    }
    return res.json();
  }

  get<T>(path: string) {
    return this.fetch<T>(path);
  }

  post<T>(path: string, body?: unknown) {
    return this.fetch<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });
  }

  patch<T>(path: string, body: unknown) {
    return this.fetch<T>(path, { method: "PATCH", body: JSON.stringify(body) });
  }

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (!res.ok) throw new Error("Credenciales inválidas");
    return res.json();
  }
}

export const api = new ApiClient();
