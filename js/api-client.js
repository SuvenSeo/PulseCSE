const PulseAPI = (() => {
  const baseUrl = localStorage.getItem("pulsecse_api_base") || "http://127.0.0.1:8088";

  const request = async (path, options = {}) => {
    const response = await fetch(`${baseUrl}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${text}`);
    }
    return response.json();
  };

  return {
    baseUrl,
    health: () => request("/health"),
    dashboard: () => request("/api/dashboard"),
    tick: () => request("/api/tick", { method: "POST" }),
    simulate: (scenario) => request(`/api/simulate/${scenario}`, { method: "POST" }),
    createAlert: (payload) => request("/api/alerts", { method: "POST", body: JSON.stringify(payload) }),
    addWatch: (symbol) => request(`/api/watchlist/${encodeURIComponent(symbol)}`, { method: "POST" }),
    removeWatch: (symbol) => request(`/api/watchlist/${encodeURIComponent(symbol)}`, { method: "DELETE" })
  };
})();

if (typeof module !== "undefined") {
  module.exports = PulseAPI;
}
