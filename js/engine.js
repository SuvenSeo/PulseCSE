const PulseEngine = (() => {
  const ALERT_LABELS = {
    price_above: "Price above",
    price_below: "Price below",
    percent_move: "Percent move",
    disclosure: "Disclosure",
    volume_spike: "Volume spike"
  };

  const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

  const toNumber = (value, fallback = 0) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  const changePercent = (company) => {
    const previous = toNumber(company.previousClose);
    if (previous === 0) return 0;
    return ((toNumber(company.price) - previous) / previous) * 100;
  };

  const volumeChangePercent = (company) => {
    const previousVolume = toNumber(company.previousVolume || company.volume);
    if (previousVolume === 0) return 0;
    return ((toNumber(company.volume) - previousVolume) / previousVolume) * 100;
  };

  const cooldownExpired = (alert, now) => {
    if (!alert.lastFiredAt) return true;
    const cooldownMinutes = toNumber(alert.cooldownMinutes, 30);
    const elapsedMs = new Date(now).getTime() - new Date(alert.lastFiredAt).getTime();
    return elapsedMs >= cooldownMinutes * 60 * 1000;
  };

  const makeEventId = (alert, company, now) => {
    const raw = `${alert.id || alert.symbol}-${company.symbol}-${alert.type}-${now}`;
    return `history-${raw.replace(/[^a-zA-Z0-9]+/g, "-").toLowerCase()}`;
  };

  const baseEvent = (alert, company, now, reason, message) => ({
    id: makeEventId(alert, company, now),
    alertId: alert.id,
    symbol: company.symbol,
    companyName: company.name,
    type: alert.type,
    target: toNumber(alert.target),
    price: toNumber(company.price),
    changePercent: Number(changePercent(company).toFixed(2)),
    volume: toNumber(company.volume),
    volumeChangePercent: Number(volumeChangePercent(company).toFixed(2)),
    note: alert.note || "No note",
    reason,
    message,
    createdAt: now
  });

  const normaliseAlert = (alert) => ({
    enabled: alert.enabled !== false,
    armed: alert.armed !== false,
    cooldownMinutes: alert.cooldownMinutes || 30,
    ...alert
  });

  const shouldFire = (alertInput, company, options = {}) => {
    const alert = normaliseAlert(alertInput);
    const now = options.now || new Date().toISOString();
    const disclosureSymbols = options.disclosureSymbols || [];
    const target = toNumber(alert.target);
    const price = toNumber(company.price);
    const previous = toNumber(company.previousClose);
    const move = changePercent(company);
    const volumeMove = volumeChangePercent(company);

    if (!alert.enabled || !alert.armed || !cooldownExpired(alert, now)) {
      return { fired: false, event: null, updatedAlert: alert };
    }

    let reason = "";
    let message = "";

    if (alert.type === "price_above" && previous < target && price >= target) {
      reason = "threshold_cross_up";
      message = `${company.symbol} crossed above LKR ${target.toFixed(2)} from LKR ${previous.toFixed(2)} to LKR ${price.toFixed(2)}.`;
    }

    if (alert.type === "price_below" && previous > target && price <= target) {
      reason = "threshold_cross_down";
      message = `${company.symbol} crossed below LKR ${target.toFixed(2)} from LKR ${previous.toFixed(2)} to LKR ${price.toFixed(2)}.`;
    }

    if (alert.type === "percent_move" && Math.abs(move) >= target) {
      reason = "daily_move_limit";
      message = `${company.symbol} moved ${move.toFixed(2)}%, crossing the ${target.toFixed(2)}% alert limit.`;
    }

    if (alert.type === "volume_spike" && volumeMove >= target) {
      reason = "volume_spike";
      message = `${company.symbol} volume rose ${volumeMove.toFixed(2)}%, above the ${target.toFixed(2)}% volume alert.`;
    }

    if (alert.type === "disclosure" && disclosureSymbols.includes(company.symbol)) {
      reason = "new_disclosure";
      message = `${company.symbol} has a new disclosure: ${company.disclosure}`;
    }

    if (!reason) {
      return { fired: false, event: null, updatedAlert: alert };
    }

    const updatedAlert = {
      ...alert,
      armed: false,
      lastFiredAt: now,
      fireCount: toNumber(alert.fireCount) + 1
    };

    return {
      fired: true,
      event: baseEvent(alert, company, now, reason, message),
      updatedAlert
    };
  };

  const rearmAlertIfConditionReset = (alertInput, company) => {
    const alert = normaliseAlert(alertInput);
    if (alert.armed) return alert;

    const price = toNumber(company.price);
    const target = toNumber(alert.target);
    const move = Math.abs(changePercent(company));
    const volumeMove = volumeChangePercent(company);

    if (alert.type === "price_above" && price < target) return { ...alert, armed: true };
    if (alert.type === "price_below" && price > target) return { ...alert, armed: true };
    if (alert.type === "percent_move" && move < target * 0.75) return { ...alert, armed: true };
    if (alert.type === "volume_spike" && volumeMove < target * 0.75) return { ...alert, armed: true };
    if (alert.type === "disclosure") return { ...alert, armed: true };

    return alert;
  };

  const evaluateAlerts = ({ alerts, companies, now = new Date().toISOString(), disclosureSymbols = [] }) => {
    const updatedAlerts = [];
    const events = [];

    alerts.forEach((alert) => {
      const company = companies.find((item) => item.symbol === alert.symbol);
      if (!company) {
        updatedAlerts.push(alert);
        return;
      }

      const rearmed = rearmAlertIfConditionReset(alert, company);
      const result = shouldFire(rearmed, company, { now, disclosureSymbols });
      updatedAlerts.push(result.updatedAlert);
      if (result.fired) events.push(result.event);
    });

    return { events, updatedAlerts };
  };

  const riskScore = (company) => {
    const history = Array.isArray(company.history) ? company.history.map((value) => toNumber(value)) : [];
    const returns = history.slice(1).map((price, index) => {
      const previous = history[index];
      return previous ? Math.abs((price - previous) / previous) * 100 : 0;
    });
    const volatility = returns.length ? returns.reduce((sum, value) => sum + value, 0) / returns.length : 0;
    const dailyMove = Math.abs(changePercent(company));
    const volumePressure = Math.abs(volumeChangePercent(company)) / 10;
    return Math.round(clamp(volatility * 12 + dailyMove * 9 + volumePressure, 0, 100));
  };

  const riskLabel = (score) => {
    if (score >= 70) return "High";
    if (score >= 40) return "Medium";
    return "Low";
  };

  const sectorSummary = (companies) => {
    const groups = companies.reduce((acc, company) => {
      if (!acc[company.sector]) acc[company.sector] = [];
      acc[company.sector].push(company);
      return acc;
    }, {});

    return Object.entries(groups).map(([sector, items]) => {
      const averageChange = items.reduce((sum, item) => sum + changePercent(item), 0) / items.length;
      const totalVolume = items.reduce((sum, item) => sum + toNumber(item.volume), 0);
      return {
        sector,
        count: items.length,
        averageChange: Number(averageChange.toFixed(2)),
        totalVolume,
        strongest: [...items].sort((a, b) => changePercent(b) - changePercent(a))[0].symbol
      };
    }).sort((a, b) => b.averageChange - a.averageChange);
  };

  const smartSuggestions = (companies, watchlist = []) => {
    return companies
      .filter((company) => watchlist.includes(company.symbol))
      .map((company) => {
        const move = changePercent(company);
        const score = riskScore(company);
        if (move > 2) {
          return {
            symbol: company.symbol,
            title: "Breakout alert suggestion",
            message: `${company.symbol} is already up ${move.toFixed(2)}%. Add a price-above alert slightly above the current price.`,
            alertType: "price_above",
            target: Number((company.price * 1.01).toFixed(2))
          };
        }
        if (move < -1.5 || score >= 55) {
          return {
            symbol: company.symbol,
            title: "Risk alert suggestion",
            message: `${company.symbol} has a ${riskLabel(score).toLowerCase()} risk score. Add a price-below alert near support.`,
            alertType: "price_below",
            target: Number((company.price * 0.98).toFixed(2))
          };
        }
        return {
          symbol: company.symbol,
          title: "Disclosure alert suggestion",
          message: `${company.symbol} is on your watchlist. Add a disclosure alert for corporate updates.`,
          alertType: "disclosure",
          target: 0
        };
      })
      .slice(0, 4);
  };

  const applyScenario = (companies, scenarioKey) => {
    const scenarios = {
      jkh_breakout: {
        symbol: "JKH.N0000",
        priceMultiplier: 1.045,
        volumeMultiplier: 1.35,
        disclosure: "Large-cap breakout and investor briefing update released.",
        disclosureEvent: false
      },
      hnb_support_break: {
        symbol: "HNB.N0000",
        priceMultiplier: 0.965,
        volumeMultiplier: 1.22,
        disclosure: "Credit-risk commentary and market sensitivity note released.",
        disclosureEvent: false
      },
      comb_disclosure: {
        symbol: "COMB.N0000",
        priceMultiplier: 1.01,
        volumeMultiplier: 1.08,
        disclosure: "New interim financial statement and board update published.",
        disclosureEvent: true
      },
      dial_volume: {
        symbol: "DIAL.N0000",
        priceMultiplier: 1.018,
        volumeMultiplier: 1.85,
        disclosure: "Network investment update added to market announcements.",
        disclosureEvent: false
      },
      market_rally: {
        symbol: "ALL",
        priceMultiplier: 1.022,
        volumeMultiplier: 1.18,
        disclosure: "Broad market momentum scenario applied.",
        disclosureEvent: false
      }
    };

    const scenario = scenarios[scenarioKey] || scenarios.market_rally;
    const disclosureSymbols = [];

    const updated = companies.map((company) => {
      const affected = scenario.symbol === "ALL" || scenario.symbol === company.symbol;
      if (!affected) return company;

      const previousPrice = toNumber(company.price);
      const previousVolume = toNumber(company.volume);
      const price = Number(Math.max(1, previousPrice * scenario.priceMultiplier).toFixed(2));
      const volume = Math.max(100, Math.round(previousVolume * scenario.volumeMultiplier));
      const disclosure = scenario.symbol === "ALL" ? company.disclosure : scenario.disclosure;

      if (scenario.disclosureEvent && scenario.symbol === company.symbol) disclosureSymbols.push(company.symbol);

      return {
        ...company,
        previousClose: previousPrice,
        previousVolume,
        price,
        volume,
        disclosure,
        signal: scenarioKey === "hnb_support_break" ? "Risk" : scenarioKey === "dial_volume" ? "Volume spike" : scenarioKey === "comb_disclosure" ? "Disclosure" : "Breakout",
        history: [...company.history.slice(-11), price]
      };
    });

    return { companies: updated, disclosureSymbols, scenario };
  };

  return {
    ALERT_LABELS,
    changePercent,
    volumeChangePercent,
    evaluateAlerts,
    shouldFire,
    riskScore,
    riskLabel,
    sectorSummary,
    smartSuggestions,
    applyScenario
  };
})();

if (typeof module !== "undefined") {
  module.exports = PulseEngine;
}
