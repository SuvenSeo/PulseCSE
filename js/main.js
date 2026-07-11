document.addEventListener("DOMContentLoaded", () => {
  const title = document.querySelector("#hero-market-status");
  if (title) {
    const companies = PulseStore.getCompanies();
    const positive = companies.filter((company) => PulseUI.changePercent(company) > 0).length;
    title.textContent = `${positive} counters green today`;
  }
});
