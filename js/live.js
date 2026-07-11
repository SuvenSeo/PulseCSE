document.addEventListener("DOMContentLoaded", () => {
  const status = document.querySelector("#api-status");
  const overview = document.querySelector("#api-overview");
  const movers = document.querySelector("#api-movers");
  const events = document.querySelector("#api-events");
  const stocks = document.querySelector("#api-stocks");
  const errorBox = document.querySelector("#api-error");

  const setError = (message) => {
    if (!errorBox) return;
    errorBox.textContent = message;
    errorBox.hidden = !message;
  };

  const render = (data) => {
    status.innerHTML = `
      <span class="status-pill live">Backend connected</span>
      <span class="muted-small">${PulseAPI.baseUrl}</span>
      <span class="muted-small">Last tick: ${data.status.last_tick_at}</span>
    `;

    overview.innerHTML = `
      <article class="metric-card"><span>${data.breadth.gainers}</span><p>Gainers</p></article>
      <article class="metric-card"><span>${data.breadth.losers}</span><p>Losers</p></article>
      <article class="metric-card"><span>${data.alerts.length}</span><p>Rules</p></article>
      <article class="metric-card"><span>${data.events.length}</span><p>Recent events</p></article>
    `;

    movers.innerHTML = data.top_movers.gainers.slice(0, 5).map((item) => `
      <article class="market-row">
        <div><strong>${item.symbol}</strong><span>${PulseUI.formatMoney(item.price)}</span></div>
        <b class="${PulseUI.changeClass(item.change_percent)}">${PulseUI.formatPercent(item.change_percent)}</b>
      </article>
    `).join("");

    events.innerHTML = data.events.length ? data.events.slice(0, 8).map((item) => `
      <article class="history-card ${item.severity}">
        <div><strong>${item.symbol}</strong><span>${PulseUI.alertLabel(item.type)} • ${item.reason}</span></div>
        <p>${item.message}</p>
        <small>${PulseUI.formatDate(item.created_at)}</small>
      </article>
    `).join("") : PulseUI.emptyState("No backend events yet. Run a scenario to trigger one.");

    stocks.innerHTML = data.stocks.slice(0, 8).map((item) => `
      <article class="company-card compact-card">
        <div class="company-card-head">
          <div><strong>${item.symbol}</strong><span>${item.name}</span></div>
          <span class="risk-badge ${String(item.risk_label).toLowerCase()}">${item.risk_label}</span>
        </div>
        <div class="stock-price-row"><b>${PulseUI.formatMoney(item.price)}</b><span class="${PulseUI.changeClass(item.change_percent)}">${PulseUI.formatPercent(item.change_percent)}</span></div>
        <p>${item.sector}</p>
      </article>
    `).join("");
  };

  const load = async () => {
    try {
      setError("");
      const data = await PulseAPI.dashboard();
      render(data);
    } catch (error) {
      status.innerHTML = `<span class="status-pill danger">Backend offline</span><span class="muted-small">Expected ${PulseAPI.baseUrl}</span>`;
      setError(`Could not reach the backend API. Start it with: python -m pulsecse api. Details: ${error.message}`);
    }
  };

  document.querySelectorAll("[data-api-scenario]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        setError("");
        const result = await PulseAPI.simulate(button.dataset.apiScenario);
        PulseUI.toast(`Scenario complete: ${result.events.length} event(s)`);
        await load();
      } catch (error) {
        setError(error.message);
      }
    });
  });

  document.querySelector("#api-tick")?.addEventListener("click", async () => {
    try {
      const result = await PulseAPI.tick();
      PulseUI.toast(`Tick complete: ${result.events.length} event(s)`);
      await load();
    } catch (error) {
      setError(error.message);
    }
  });

  document.querySelector("#save-api-base")?.addEventListener("click", () => {
    const value = document.querySelector("#api-base-input").value.trim();
    if (value) localStorage.setItem("pulsecse_api_base", value.replace(/\/$/, ""));
    window.location.reload();
  });

  document.querySelector("#api-base-input").value = PulseAPI.baseUrl;
  load();
});
