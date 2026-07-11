const PulseStore = (() => {
  const keys = {
    companies: "pulsecse_companies_v2",
    watchlist: "pulsecse_watchlist_v2",
    alerts: "pulsecse_alerts_v2",
    history: "pulsecse_history_v2"
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

  const normaliseAlert = (alert) => ({
    enabled: alert.enabled !== false,
    armed: alert.armed !== false,
    cooldownMinutes: alert.cooldownMinutes || 30,
    fireCount: alert.fireCount || 0,
    ...alert
  });

  const getCompanies = () => read(keys.companies, PulseData.companies);
  const saveCompanies = (companies) => write(keys.companies, companies);

  const getWatchlist = () => read(keys.watchlist, PulseData.defaultWatchlist);
  const saveWatchlist = (watchlist) => write(keys.watchlist, watchlist);

  const getAlerts = () => read(keys.alerts, []).map(normaliseAlert);
  const saveAlerts = (alerts) => write(keys.alerts, alerts.map(normaliseAlert));

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
    alerts.unshift(normaliseAlert(alert));
    saveAlerts(alerts);
    return alerts;
  };

  const updateAlert = (id, patch) => {
    const alerts = getAlerts().map((alert) => alert.id === id ? normaliseAlert({ ...alert, ...patch }) : alert);
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
    saveHistory([...list, ...history].slice(0, 120));
  };

  const reset = () => {
    Object.values(keys).forEach((key) => localStorage.removeItem(key));
  };

  const randomBetween = (min, max) => Math.random() * (max - min) + min;

  const evaluateAlerts = (companies = getCompanies(), options = {}) => {
    const result = PulseEngine.evaluateAlerts({
      alerts: getAlerts(),
      companies,
      now: options.now || new Date().toISOString(),
      disclosureSymbols: options.disclosureSymbols || []
    });

    saveAlerts(result.updatedAlerts);
    if (result.events.length > 0) addHistory(result.events);
    return result.events;
  };

  const simulateMarketTick = () => {
    const disclosureSymbols = [];
    const companies = getCompanies().map((company) => {
      const movePercent = randomBetween(-2.4, 3.1);
      const previousPrice = company.price;
      const previousVolume = company.volume;
      const nextPrice = Math.max(1, previousPrice * (1 + movePercent / 100));
      const nextVolume = Math.max(100, Math.round(company.volume * (1 + randomBetween(-0.18, 0.28))));
      const history = [...company.history.slice(-11), Number(nextPrice.toFixed(2))];
      const disclosureEvent = Math.random() > 0.88;
      if (disclosureEvent) disclosureSymbols.push(company.symbol);

      return {
        ...company,
        previousClose: previousPrice,
        previousVolume,
        price: Number(nextPrice.toFixed(2)),
        volume: nextVolume,
        history,
        disclosure: disclosureEvent ? `New simulated corporate disclosure released for ${company.symbol}.` : company.disclosure
      };
    });

    saveCompanies(companies);
    const fired = evaluateAlerts(companies, { disclosureSymbols });
    return { companies, fired, disclosureSymbols };
  };

  const applyScenario = (scenarioKey) => {
    const result = PulseEngine.applyScenario(getCompanies(), scenarioKey);
    saveCompanies(result.companies);
    const fired = evaluateAlerts(result.companies, { disclosureSymbols: result.disclosureSymbols });
    return { ...result, fired };
  };

  const createAlertForCompany = (symbol, type, target, note = "Quick alert") => addAlert({
    id: `alert-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    symbol,
    type,
    target: Number(target || 0),
    note,
    enabled: true,
    armed: true,
    cooldownMinutes: 30,
    fireCount: 0,
    createdAt: new Date().toISOString()
  });

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
    updateAlert,
    removeAlert,
    addHistory,
    reset,
    simulateMarketTick,
    evaluateAlerts,
    applyScenario,
    createAlertForCompany
  };
})();
