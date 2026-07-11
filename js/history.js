document.addEventListener("DOMContentLoaded", () => {
  const list = document.querySelector("#history-list");
  const countPill = document.querySelector("#history-count-pill");
  const clearButton = document.querySelector("#clear-history");
  const exportButton = document.querySelector("#export-history");
  const exportCsvButton = document.querySelector("#export-csv");

  const render = () => {
    const history = PulseStore.getHistory();
    countPill.textContent = `${history.length} events`;

    if (history.length === 0) {
      list.innerHTML = PulseUI.emptyState("No alert history yet. Use the Alerts page to test alert rules.");
      return;
    }

    list.innerHTML = history.map((event) => `
      <article class="timeline-item">
        <strong>${event.symbol} - ${PulseUI.alertLabel(event.type)}</strong>
        <span>${event.message}</span><br>
        <span>Price: ${PulseUI.formatMoney(event.price)} | Move: ${PulseUI.formatPercent(event.changePercent)} | Target: ${PulseUI.targetDisplay(event)}</span><br>
        <span>Note: ${event.note} | ${PulseUI.formatDate(event.createdAt)}</span>
      </article>
    `).join("");
  };

  clearButton.addEventListener("click", () => {
    PulseStore.saveHistory([]);
    PulseUI.toast("Alert history cleared.");
    render();
  });

  exportButton.addEventListener("click", () => {
    const history = PulseStore.getHistory();
    const blob = new Blob([JSON.stringify(history, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "pulsecse-alert-history.json";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    PulseUI.toast("History exported as JSON.");
  });


  exportCsvButton.addEventListener("click", () => {
    const history = PulseStore.getHistory();
    const header = ["createdAt", "symbol", "type", "target", "price", "changePercent", "reason", "message"];
    const rows = history.map((event) => header.map((key) => `"${String(event[key] ?? "").replaceAll('"', '""')}"`).join(","));
    const blob = new Blob([[header.join(","), ...rows].join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "pulsecse-alert-history.csv";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    PulseUI.toast("History exported as CSV.");
  });

  render();
});
