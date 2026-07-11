const PulseUI = (() => {
  const pages = [
    { href: "index.html", label: "Home" },
    { href: "dashboard.html", label: "Dashboard" },
    { href: "alerts.html", label: "Alerts" },
    { href: "companies.html", label: "Companies" },
    { href: "simulator.html", label: "Simulator" },
    { href: "live.html", label: "Live API" },
    { href: "history.html", label: "History" },
    { href: "about.html", label: "About" }
  ];

  const formatMoney = (value) => `LKR ${Number(value).toLocaleString("en-LK", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatNumber = (value) => Number(value).toLocaleString("en-LK");
  const formatPercent = (value) => `${Number(value).toFixed(2)}%`;

  const changePercent = (company) => {
    if (!company.previousClose) return 0;
    return ((company.price - company.previousClose) / company.previousClose) * 100;
  };

  const changeClass = (value) => {
    if (value > 0) return "positive-text";
    if (value < 0) return "negative-text";
    return "warning-text";
  };

  const alertLabel = (type) => {
    const labels = {
      price_above: "Price above",
      price_below: "Price below",
      percent_move: "Percent move",
      disclosure: "Disclosure",
      volume_spike: "Volume spike",
      news_keyword: "Keyword",
      risk_score: "Risk score"
    };
    return labels[type] || type;
  };

  const formatDate = (iso) => {
    const date = new Date(iso);
    return date.toLocaleString("en-LK", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const toast = (message) => {
    const region = document.querySelector("#toast-region");
    if (!region) return;
    const item = document.createElement("div");
    item.className = "toast";
    item.textContent = message;
    region.appendChild(item);
    window.setTimeout(() => item.remove(), 3600);
  };

  const renderNav = () => {
    const nav = document.querySelector('[data-component="nav"]');
    if (!nav) return;
    const current = window.location.pathname.split("/").pop() || "index.html";

    nav.innerHTML = `
      <a class="brand" href="index.html" aria-label="PulseCSE home">
        <img src="assets/logo.svg" alt="" />
        <span>PulseCSE</span>
      </a>
      <button class="nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false"><span></span></button>
      <nav class="nav-links" aria-label="Primary navigation">
        ${pages.map((page) => `<a class="nav-link ${page.href === current ? "active" : ""}" href="${page.href}">${page.label}</a>`).join("")}
      </nav>
    `;

    const toggle = nav.querySelector(".nav-toggle");
    const links = nav.querySelector(".nav-links");
    toggle.addEventListener("click", () => {
      links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", links.classList.contains("open") ? "true" : "false");
    });
  };

  const emptyState = (message) => `<div class="empty-state">${message}</div>`;

  const drawChart = (canvas, series) => {
    if (!canvas || !series || series.length < 2) return;
    const context = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    const padding = 30;
    const max = Math.max(...series);
    const min = Math.min(...series);
    const spread = max - min || 1;

    context.clearRect(0, 0, width, height);
    context.lineWidth = 1;
    context.strokeStyle = "rgba(255, 255, 255, 0.08)";

    for (let i = 0; i < 5; i += 1) {
      const y = padding + ((height - padding * 2) / 4) * i;
      context.beginPath();
      context.moveTo(padding, y);
      context.lineTo(width - padding, y);
      context.stroke();
    }

    context.lineWidth = 4;
    context.strokeStyle = "#22d3ee";
    context.beginPath();

    series.forEach((value, index) => {
      const x = padding + ((width - padding * 2) / (series.length - 1)) * index;
      const y = height - padding - ((value - min) / spread) * (height - padding * 2);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });

    context.stroke();

    context.lineWidth = 2;
    context.strokeStyle = "#f5c451";
    context.beginPath();
    series.forEach((value, index) => {
      const x = padding + ((width - padding * 2) / (series.length - 1)) * index;
      const y = height - padding - ((value - min) / spread) * (height - padding * 2);
      if (index === 0 || index === series.length - 1) {
        context.moveTo(x + 6, y);
        context.arc(x, y, 6, 0, Math.PI * 2);
      }
    });
    context.stroke();
  };


  const getQueryParam = (name) => new URLSearchParams(window.location.search).get(name);

  const targetDisplay = (eventOrAlert) => {
    if (eventOrAlert.type === "percent_move" || eventOrAlert.type === "volume_spike") return formatPercent(eventOrAlert.target);
    if (eventOrAlert.type === "disclosure") return "Disclosure update";
    return formatMoney(eventOrAlert.target);
  };

  const init = () => {
    renderNav();
  };

  document.addEventListener("DOMContentLoaded", init);

  return {
    formatMoney,
    formatNumber,
    formatPercent,
    changePercent,
    changeClass,
    alertLabel,
    formatDate,
    toast,
    emptyState,
    drawChart,
    getQueryParam,
    targetDisplay
  };
})();
