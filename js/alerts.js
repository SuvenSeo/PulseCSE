document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#alert-form");
  const symbolSelect = document.querySelector("#symbol");
  const typeSelect = document.querySelector("#alert-type");
  const targetInput = document.querySelector("#target");
  const noteInput = document.querySelector("#note");
  const tableBody = document.querySelector("#alerts-table tbody");
  const countPill = document.querySelector("#alert-count-pill");
  const seedButton = document.querySelector("#seed-alerts");
  const testButton = document.querySelector("#test-alerts");

  const populateSymbols = () => {
    const companies = PulseStore.getCompanies();
    symbolSelect.innerHTML = companies.map((company) => `
      <option value="${company.symbol}">${company.symbol} - ${company.name}</option>
    `).join("");
  };

  const renderAlerts = () => {
    const alerts = PulseStore.getAlerts();
    const companies = PulseStore.getCompanies();
    countPill.textContent = `${alerts.length} active`;

    if (alerts.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="5">${PulseUI.emptyState("No alerts saved yet. Create one using the form.")}</td></tr>`;
      return;
    }

    tableBody.innerHTML = alerts.map((alert) => {
      const company = companies.find((item) => item.symbol === alert.symbol);
      const target = alert.type === "disclosure" ? "Any new update" : alert.type === "percent_move" ? PulseUI.formatPercent(alert.target) : PulseUI.formatMoney(alert.target);
      return `
        <tr>
          <td><span class="symbol-pill">${alert.symbol}</span><br><span class="card-meta">${company ? company.name : "Unknown"}</span></td>
          <td>${PulseUI.alertLabel(alert.type)}</td>
          <td>${target}</td>
          <td>${alert.note || "No note"}</td>
          <td><button class="icon-btn" data-delete="${alert.id}" aria-label="Delete alert">x</button></td>
        </tr>
      `;
    }).join("");

    tableBody.querySelectorAll("[data-delete]").forEach((button) => {
      button.addEventListener("click", () => {
        PulseStore.removeAlert(button.dataset.delete);
        PulseUI.toast("Alert removed.");
        renderAlerts();
      });
    });
  };

  typeSelect.addEventListener("change", () => {
    if (typeSelect.value === "disclosure") {
      targetInput.value = "0";
      targetInput.disabled = true;
    } else {
      targetInput.disabled = false;
      if (targetInput.value === "0") targetInput.value = "";
    }
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const alert = {
      id: `alert-${Date.now()}-${Math.random().toString(16).slice(2)}`,
      symbol: symbolSelect.value,
      type: typeSelect.value,
      target: Number(targetInput.value || 0),
      note: noteInput.value.trim(),
      createdAt: new Date().toISOString()
    };

    PulseStore.addAlert(alert);
    PulseStore.addToWatchlist(alert.symbol);
    form.reset();
    targetInput.disabled = false;
    PulseUI.toast("Alert saved and company added to watchlist.");
    renderAlerts();
  });

  seedButton.addEventListener("click", () => {
    PulseStore.saveAlerts(PulseData.sampleAlerts);
    PulseData.sampleAlerts.forEach((alert) => PulseStore.addToWatchlist(alert.symbol));
    PulseUI.toast("Sample alerts loaded.");
    renderAlerts();
  });

  testButton.addEventListener("click", () => {
    const result = PulseStore.simulateMarketTick();
    if (result.fired.length > 0) {
      PulseUI.toast(`${result.fired.length} alert(s) fired. Check History.`);
    } else {
      PulseUI.toast("Test completed. No alert fired this time.");
    }
    renderAlerts();
  });

  populateSymbols();
  renderAlerts();
});
