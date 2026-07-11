const PulseStore = (() => {
  const keys = {
    companies: "pulsecse_companies_v1",
    watchlist: "pulsecse_watchlist_v1",
    alerts: "pulsecse_alerts_v1",
    history: "pulsecse_history_v1"
  };

  const clone = (value) => JSON.parse(JSON.stringify(value));

  const read = (key, fallback) => {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : clone(fallback);
    } catch (error) {
      console.warn("LocalStorage read failed", error);
      return clone(fallback);
    }
  };

  const write = (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.warn("LocalStorage write failed", error);
    }
  };

  const getCompanies = () => read(keys.companies, PulseData.companies);
  const saveCompanies = (companies) => write(keys.companies, companies);

  const getWatchlist = () => read(keys.watchlist, PulseData.defaultWatchlist);
  const saveWatchlist = (watchlist) => write(keys.watchlist, watchlist);

  const getAlerts = () => read(keys.alerts, []);
  const saveAlerts = (alerts) => write(keys.alerts, alerts);

  const getHistory = () => read(keys.history, []);
  const saveHistory = (history) => write(keys.history, history);

  const findCompany = (symbol) => getCompanies().find((company) => company.symbol === symbol);

  const addToWatchlist = (symbol) => {
    const watchlist = getWatchlist();
    if (!watchlist.includes(symbol)) {
      watchlist.push(symbol);
      saveWatchlist(watchlist);
    }
    return watchlist;
  };

  const removeFromWatchlist = (symbol) => {
    const updated = getWatchlist().filter((item) => item !== symbol);
    saveWatchlist(updated);
    return updated;
  };

  const addAlert = (alert) => {
    const alerts = getAlerts();
    alerts.unshift(alert);
    saveAlerts(alerts);
    return alerts;
  };

  const removeAlert = (id) => {
    const updated = getAlerts().filter((alert) => alert.id !== id);
    saveAlerts(updated);
    return updated;
  };

  const addHistory = (events) => {
    const history = getHistory();
    const list = Array.isArray(events) ? events : [events];
    saveHistory([...list, ...history].slice(0, 80));
  };

  const reset = () => {
    localStorage.removeItem(keys.companies);
    localStorage.removeItem(keys.watchlist);
    localStorage.removeItem(keys.alerts);
    localStorage.removeItem(keys.history);
  };

  const randomBetween = (min, max) => Math.random() * (max - min) + min;

  const simulateMarketTick = () => {
    const companies = getCompanies().map((company) => {
      const movePercent = randomBetween(-2.4, 3.1);
      const previousPrice = company.price;
      const nextPrice = Math.max(1, previousPrice * (1 + movePercent / 100));
      const nextVolume = Math.max(100, Math.round(company.volume * (1 + randomBetween(-0.18, 0.28))));
      const history = [...company.history.slice(-9), Number(nextPrice.toFixed(2))];

      return {
        ...company,
        previousClose: previousPrice,
        price: Number(nextPrice.toFixed(2)),
        volume: nextVolume,
        history
      };
    });

    saveCompanies(companies);
    const fired = evaluateAlerts(companies);
    if (fired.length > 0) {
      addHistory(fired);
    }
    return { companies, fired };
  };

  const evaluateAlerts = (companies = getCompanies()) => {
    const alerts = getAlerts();
    const now = new Date().toISOString();

    return alerts.flatMap((alert) => {
      const company = companies.find((item) => item.symbol === alert.symbol);
      if (!company) return [];

      const price = Number(company.price);
      const previous = Number(company.previousClose);
      const changePercent = previous === 0 ? 0 : ((price - previous) / previous) * 100;
      const target = Number(alert.target);
      let fired = false;
      let message = "";

      if (alert.type === "price_above" && price >= target && previous < target) {
        fired = true;
        message = `${company.symbol} crossed above LKR ${target.toFixed(2)} and is now LKR ${price.toFixed(2)}.`;
      }

      if (alert.type === "price_below" && price <= target && previous > target) {
        fired = true;
        message = `${company.symbol} crossed below LKR ${target.toFixed(2)} and is now LKR ${price.toFixed(2)}.`;
      }

      if (alert.type === "percent_move" && Math.abs(changePercent) >= target) {
        fired = true;
        message = `${company.symbol} moved ${changePercent.toFixed(2)}% in the latest market tick.`;
      }

      if (alert.type === "disclosure") {
        fired = Math.random() > 0.58;
        message = `${company.symbol} has a simulated disclosure update: ${company.disclosure}`;
      }

      if (!fired) return [];

      return [{
        id: `history-${Date.now()}-${Math.random().toString(16).slice(2)}`,
        alertId: alert.id,
        symbol: company.symbol,
        companyName: company.name,
        type: alert.type,
        target: alert.target,
        price,
        changePercent: Number(changePercent.toFixed(2)),
        note: alert.note || "No note",
        message,
        createdAt: now
      }];
    });
  };

  return {
    getCompanies,
    saveCompanies,
    getWatchlist,
    saveWatchlist,
    getAlerts,
    saveAlerts,
    getHistory,
    saveHistory,
    findCompany,
    addToWatchlist,
    removeFromWatchlist,
    addAlert,
    removeAlert,
    addHistory,
    reset,
    simulateMarketTick,
    evaluateAlerts
  };
})();
