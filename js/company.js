document.addEventListener("DOMContentLoaded", () => {
  const symbol = PulseUI.getQueryParam("symbol") || "JKH.N0000";
  const company = PulseStore.findCompany(symbol);

  const title = document.querySelector("#company-title");
  const description = document.querySelector("#company-description");
  const watchButton = document.querySelector("#watch-toggle");
  const canvas = document.querySelector("#company-canvas");

  if (!company) {
    title.textContent = "Company not found";
    description.textContent = "Go back to the company directory and choose a valid symbol.";
    return;
  }

  const render = () => {
    const latest = PulseStore.findCompany(symbol);
    const watchlist = PulseStore.getWatchlist();
    const change = PulseUI.changePercent(latest);
    const risk = PulseEngine.riskScore(latest);
    const volumeChange = PulseEngine.volumeChangePercent(latest);

    document.title = `${latest.symbol} | PulseCSE`;
    title.textContent = `${latest.symbol} - ${latest.name}`;
    description.textContent = latest.description;
    watchButton.textContent = watchlist.includes(latest.symbol) ? "Remove from Watchlist" : "Add to Watchlist";
    document.querySelector("#detail-price").textContent = PulseUI.formatMoney(latest.price);
    document.querySelector("#detail-change").textContent = `${PulseUI.formatPercent(change)} today`;
    document.querySelector("#detail-change").className = PulseUI.changeClass(change);
    document.querySelector("#detail-risk").textContent = risk;
    document.querySelector("#detail-risk-label").textContent = `${PulseEngine.riskLabel(risk)} risk based on price/volume movement`;
    document.querySelector("#detail-volume").textContent = PulseUI.formatNumber(latest.volume);
    document.querySelector("#detail-volume-change").textContent = `${PulseUI.formatPercent(volumeChange)} vs previous`;
    document.querySelector("#detail-marketcap").textContent = latest.marketCap;
    document.querySelector("#detail-sector").textContent = latest.sector;
    document.querySelector("#detail-signal").textContent = latest.signal;

    PulseUI.drawChart(canvas, latest.history);

    document.querySelector("#company-disclosures").innerHTML = `
      <article class="timeline-item">
        <strong>${latest.symbol} disclosure monitor</strong>
        <span>${latest.disclosure}</span><br>
        <span>Prototype note: this is mock disclosure content for the demo flow.</span>
      </article>
      <article class="timeline-item">
        <strong>Why this matters</strong>
        <span>Disclosure alerts help users react to corporate announcements without manually checking multiple pages.</span>
      </article>
    `;

    const peers = PulseStore.getCompanies().filter((item) => item.sector === latest.sector && item.symbol !== latest.symbol).slice(0, 5);
    document.querySelector("#peer-list").innerHTML = peers.length ? peers.map((peer) => `
      <a class="peer-item" href="company.html?symbol=${encodeURIComponent(peer.symbol)}">
        <span><strong>${peer.symbol}</strong><br><small>${peer.name}</small></span>
        <b class="${PulseUI.changeClass(PulseUI.changePercent(peer))}">${PulseUI.formatPercent(PulseUI.changePercent(peer))}</b>
      </a>
    `).join("") : PulseUI.emptyState("No same-sector peers in demo data.");
  };

  watchButton.addEventListener("click", () => {
    const current = PulseStore.getWatchlist();
    if (current.includes(symbol)) {
      PulseStore.removeFromWatchlist(symbol);
      PulseUI.toast(`${symbol} removed from watchlist.`);
    } else {
      PulseStore.addToWatchlist(symbol);
      PulseUI.toast(`${symbol} added to watchlist.`);
    }
    render();
  });

  document.querySelectorAll("[data-quick]").forEach((button) => {
    button.addEventListener("click", () => {
      const latest = PulseStore.findCompany(symbol);
      const action = button.dataset.quick;
      if (action === "above") PulseStore.createAlertForCompany(symbol, "price_above", Number((latest.price * 1.01).toFixed(2)), "Quick breakout alert");
      if (action === "below") PulseStore.createAlertForCompany(symbol, "price_below", Number((latest.price * 0.98).toFixed(2)), "Quick support alert");
      if (action === "move") PulseStore.createAlertForCompany(symbol, "percent_move", 2.5, "Quick momentum alert");
      if (action === "disclosure") PulseStore.createAlertForCompany(symbol, "disclosure", 0, "Quick disclosure alert");
      PulseStore.addToWatchlist(symbol);
      PulseUI.toast("Quick alert created. View it on the Alerts page.");
      render();
    });
  });

  render();
});
