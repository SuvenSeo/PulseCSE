document.addEventListener("DOMContentLoaded", () => {
  const grid = document.querySelector("#company-grid");
  const searchInput = document.querySelector("#company-search");
  const sectorFilter = document.querySelector("#sector-filter");

  const populateSectors = () => {
    const sectors = [...new Set(PulseStore.getCompanies().map((company) => company.sector))].sort();
    sectorFilter.innerHTML = `<option value="all">All sectors</option>${sectors.map((sector) => `<option value="${sector}">${sector}</option>`).join("")}`;
  };

  const renderCompanies = () => {
    const companies = PulseStore.getCompanies();
    const watchlist = PulseStore.getWatchlist();
    const query = searchInput.value.trim().toLowerCase();
    const sector = sectorFilter.value;

    const filtered = companies.filter((company) => {
      const matchesQuery = `${company.symbol} ${company.name} ${company.sector}`.toLowerCase().includes(query);
      const matchesSector = sector === "all" || company.sector === sector;
      return matchesQuery && matchesSector;
    });

    if (filtered.length === 0) {
      grid.innerHTML = PulseUI.emptyState("No companies match the current search or filter.");
      return;
    }

    grid.innerHTML = filtered.map((company) => {
      const change = PulseUI.changePercent(company);
      const risk = PulseEngine.riskScore(company);
      const inWatchlist = watchlist.includes(company.symbol);
      return `
        <article class="company-card">
          <div class="company-card-header">
            <span class="symbol-pill">${company.symbol}</span>
            <span class="status-pill ${risk >= 60 ? "warning" : change >= 0 ? "good" : ""}">Risk ${risk}</span>
          </div>
          <div>
            <h2>${company.name}</h2>
            <p>${company.description}</p>
          </div>
          <div class="price-row">
            <div>
              <span class="card-meta">Last price</span>
              <strong>${PulseUI.formatMoney(company.price)}</strong>
            </div>
            <span class="${PulseUI.changeClass(change)}">${PulseUI.formatPercent(change)}</span>
          </div>
          <div class="card-meta">Sector: ${company.sector}<br>Volume: ${PulseUI.formatNumber(company.volume)}<br>Market cap: ${company.marketCap}<br>Signal: ${company.signal}</div>
          <div class="card-actions">
            <button class="btn ${inWatchlist ? "btn-secondary" : "btn-primary"}" data-watch="${company.symbol}">
              ${inWatchlist ? "Remove" : "Watch"}
            </button>
            <a class="btn btn-secondary" href="company.html?symbol=${encodeURIComponent(company.symbol)}">Details</a>
          </div>
        </article>
      `;
    }).join("");

    grid.querySelectorAll("[data-watch]").forEach((button) => {
      button.addEventListener("click", () => {
        const symbol = button.dataset.watch;
        const current = PulseStore.getWatchlist();
        if (current.includes(symbol)) {
          PulseStore.removeFromWatchlist(symbol);
          PulseUI.toast(`${symbol} removed from watchlist.`);
        } else {
          PulseStore.addToWatchlist(symbol);
          PulseUI.toast(`${symbol} added to watchlist.`);
        }
        renderCompanies();
      });
    });
  };

  searchInput.addEventListener("input", renderCompanies);
  sectorFilter.addEventListener("change", renderCompanies);

  populateSectors();
  renderCompanies();
});
