document.addEventListener("DOMContentLoaded", () => {
  const output = document.querySelector("#scenario-output");
  const status = document.querySelector("#scenario-status");
  const suggestions = document.querySelector("#suggestion-list");
  const loadDemoButton = document.querySelector("#load-demo-alerts");
  const randomButton = document.querySelector("#run-random-tick");

  const renderSuggestions = () => {
    const items = PulseEngine.smartSuggestions(PulseStore.getCompanies(), PulseStore.getWatchlist());
    suggestions.innerHTML = items.length ? items.map((item) => `
      <article class="suggestion-item">
        <strong>${item.symbol}</strong>
        <span>${item.title}</span>
        <p>${item.message}</p>
        <button class="btn btn-secondary full-width" data-suggest-symbol="${item.symbol}" data-suggest-type="${item.alertType}" data-suggest-target="${item.target}">Add suggestion</button>
      </article>
    `).join("") : PulseUI.emptyState("Add companies to your watchlist to get suggestions.");

    suggestions.querySelectorAll("[data-suggest-symbol]").forEach((button) => {
      button.addEventListener("click", () => {
        PulseStore.createAlertForCompany(button.dataset.suggestSymbol, button.dataset.suggestType, button.dataset.suggestTarget, "Smart suggestion");
        PulseUI.toast("Suggested alert created.");
        renderSuggestions();
      });
    });
  };

  const renderEvents = (title, result) => {
    status.textContent = `${result.fired.length} fired`;
    if (result.fired.length === 0) {
      output.innerHTML = `
        <article class="timeline-item">
          <strong>${title}</strong>
          <span>Scenario completed, but no alert fired. Load demo alerts or create matching alerts first.</span>
        </article>
      `;
      return;
    }

    output.innerHTML = result.fired.map((event) => `
      <article class="timeline-item">
        <strong>${event.symbol} - ${PulseUI.alertLabel(event.type)}</strong>
        <span>${event.message}</span><br>
        <span>Reason: ${event.reason} | Price: ${PulseUI.formatMoney(event.price)} | Target: ${PulseUI.targetDisplay(event)}</span>
      </article>
    `).join("");
  };

  document.querySelectorAll("[data-scenario]").forEach((button) => {
    button.addEventListener("click", () => {
      const result = PulseStore.applyScenario(button.dataset.scenario);
      renderEvents(button.textContent.trim(), result);
      renderSuggestions();
      PulseUI.toast(`${result.fired.length} alert(s) fired in scenario.`);
    });
  });

  randomButton.addEventListener("click", () => {
    const result = PulseStore.simulateMarketTick();
    renderEvents("Random market tick", result);
    renderSuggestions();
    PulseUI.toast("Random market tick applied.");
  });

  loadDemoButton.addEventListener("click", () => {
    PulseStore.saveAlerts(PulseData.sampleAlerts);
    PulseData.sampleAlerts.forEach((alert) => PulseStore.addToWatchlist(alert.symbol));
    PulseUI.toast("Demo alerts loaded for all scenarios.");
    status.textContent = "Demo loaded";
    renderSuggestions();
  });

  output.innerHTML = PulseUI.emptyState("Load demo alerts, then run a scenario to see deterministic alert results.");
  renderSuggestions();
});
