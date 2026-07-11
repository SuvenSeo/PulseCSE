document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.querySelector("#watchlist-table tbody");
  const recentHistory = document.querySelector("#recent-history");
  const disclosureList = document.querySelector("#disclosure-list");
  const watchlistValue = document.querySelector("#watchlist-value");
  const watchlistChange = document.querySelector("#watchlist-change");
  const activeAlerts = document.querySelector("#active-alerts");
  const triggeredToday = document.querySelector("#triggered-today");
  const disclosureCount = document.querySelector("#disclosure-count");
  const simulateButton = document.querySelector("#simulate-market");
  const resetButton = document.querySelector("#reset-demo");
  const canvas = document.querySelector("#market-canvas");
  const sectorHeatmap = document.querySelector("#sector-heatmap");
  const dashboardSuggestions = document.querySelector("#dashboard-suggestions");

  const renderStats = (companies, watchlist, history, alerts) => {
    const tracked = companies.filter((company) => watchlist.includes(company.symbol));
    const total = tracked.reduce((sum, company) => sum + company.price, 0);
    const previousTotal = tracked.reduce((sum, company) => sum + company.previousClose, 0);
    const change = previousTotal ? ((total - previousTotal) / previousTotal) * 100 : 0;
    const today = new Date().toDateString();
    const todayEvents = history.filter((event) => new Date(event.createdAt).toDateString() === today);

    watchlistValue.textContent = PulseUI.formatMoney(total);
    watchlistChange.textContent = `${PulseUI.formatPercent(change)} watchlist movement`;
    watchlistChange.className = PulseUI.changeClass(change);
    activeAlerts.textContent = alerts.length;
    triggeredToday.textContent = todayEvents.length;
    disclosureCount.textContent = companies.filter((company) => company.disclosure).length;
  };

  const renderWatchlist = (companies, watchlist) => {
    const tracked = companies.filter((company) => watchlist.includes(company.symbol));

    if (tracked.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6">${PulseUI.emptyState("No watchlist items yet. Add companies from the Companies page.")}</td></tr>`;
      return;
    }

    tableBody.innerHTML = tracked.map((company) => {
      const change = PulseUI.changePercent(company);
      return `
        <tr>
          <td><a class="symbol-pill" href="company.html?symbol=${encodeURIComponent(company.symbol)}">${company.symbol}</a></td>
          <td>${company.name}<br><span class="card-meta">${company.sector}</span></td>
          <td>${PulseUI.formatMoney(company.price)}</td>
          <td class="${PulseUI.changeClass(change)}">${PulseUI.formatPercent(change)}</td>
          <td>${company.signal}</td>
          <td><button class="icon-btn" data-remove="${company.symbol}" aria-label="Remove ${company.symbol} from watchlist">x</button></td>
        </tr>
      `;
    }).join("");

    tableBody.querySelectorAll("[data-remove]").forEach((button) => {
      button.addEventListener("click", () => {
        PulseStore.removeFromWatchlist(button.dataset.remove);
        PulseUI.toast(`${button.dataset.remove} removed from watchlist.`);
        render();
      });
    });
  };

  const renderHistory = (history) => {
    const recent = history.slice(0, 5);
    if (recent.length === 0) {
      recentHistory.innerHTML = PulseUI.emptyState("No fired alerts yet. Create alerts and simulate a market tick.");
      return;
    }

    recentHistory.innerHTML = recent.map((event) => `
      <article class="timeline-item">
        <strong>${event.symbol} - ${PulseUI.alertLabel(event.type)}</strong>
        <span>${event.message}</span><br>
        <span>${PulseUI.formatDate(event.createdAt)}</span>
      </article>
    `).join("");
  };

  const renderDisclosures = (companies) => {
    disclosureList.innerHTML = companies.slice(0, 5).map((company) => `
      <article class="disclosure-item">
        <strong>${company.symbol}</strong>
        <span>${company.disclosure}</span>
      </article>
    `).join("");
  };

  const renderChart = (companies, watchlist) => {
    const tracked = companies.filter((company) => watchlist.includes(company.symbol));
    const maxLength = Math.max(...tracked.map((company) => company.history.length), 1);
    const series = Array.from({ length: maxLength }).map((_, index) => {
      const values = tracked.map((company) => company.history[index] || company.history[company.history.length - 1]);
      return values.reduce((sum, value) => sum + value, 0) / values.length;
    });
    PulseUI.drawChart(canvas, series);
  };


  const renderHeatmap = (companies) => {
    const sectors = PulseEngine.sectorSummary(companies);
    sectorHeatmap.innerHTML = sectors.map((sector) => `
      <article class="heatmap-card ${sector.averageChange >= 0 ? "positive" : "negative"}">
        <strong>${sector.sector}</strong>
        <span>${PulseUI.formatPercent(sector.averageChange)} average</span>
        <small>${sector.count} counters | strongest: ${sector.strongest}</small>
      </article>
    `).join("");
  };

  const renderSuggestions = (companies, watchlist) => {
    const suggestions = PulseEngine.smartSuggestions(companies, watchlist);
    dashboardSuggestions.innerHTML = suggestions.length ? suggestions.map((item) => `
      <article class="suggestion-item">
        <strong>${item.symbol}</strong>
        <span>${item.title}</span>
        <p>${item.message}</p>
      </article>
    `).join("") : PulseUI.emptyState("Add companies to your watchlist to receive suggestions.");
  };

  const render = () => {
    const companies = PulseStore.getCompanies();
    const watchlist = PulseStore.getWatchlist();
    const history = PulseStore.getHistory();
    const alerts = PulseStore.getAlerts();

    renderStats(companies, watchlist, history, alerts);
    renderWatchlist(companies, watchlist);
    renderHistory(history);
    renderDisclosures(companies);
    renderChart(companies, watchlist);
    renderHeatmap(companies);
    renderSuggestions(companies, watchlist);
  };

  simulateButton.addEventListener("click", () => {
    const result = PulseStore.simulateMarketTick();
    if (result.fired.length > 0) {
      PulseUI.toast(`${result.fired.length} alert(s) fired from latest market tick.`);
    } else {
      PulseUI.toast("Market tick complete. No alert rules fired this time.");
    }
    render();
  });

  resetButton.addEventListener("click", () => {
    PulseStore.reset();
    PulseUI.toast("Demo data reset to default state.");
    render();
  });

  render();
});
