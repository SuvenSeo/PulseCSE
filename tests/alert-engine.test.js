const assert = require("node:assert/strict");
const PulseEngine = require("../js/engine.js");

const baseCompany = {
  symbol: "JKH.N0000",
  name: "John Keells Holdings PLC",
  sector: "Capital Goods",
  previousClose: 189,
  price: 191,
  previousVolume: 1000,
  volume: 1200,
  disclosure: "Board update released.",
  history: [180, 184, 189, 191]
};

const run = (name, fn) => {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    throw error;
  }
};

run("price_above fires only when crossing upward", () => {
  const result = PulseEngine.evaluateAlerts({
    alerts: [{ id: "a1", symbol: "JKH.N0000", type: "price_above", target: 190, armed: true, enabled: true }],
    companies: [baseCompany],
    now: "2026-07-11T20:00:00.000Z"
  });
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].reason, "threshold_cross_up");
  assert.equal(result.updatedAlerts[0].armed, false);
});

run("price_above does not fire when already above threshold", () => {
  const result = PulseEngine.evaluateAlerts({
    alerts: [{ id: "a1", symbol: "JKH.N0000", type: "price_above", target: 190, armed: true, enabled: true }],
    companies: [{ ...baseCompany, previousClose: 191, price: 192 }],
    now: "2026-07-11T20:00:00.000Z"
  });
  assert.equal(result.events.length, 0);
});

run("price_below fires when crossing downward", () => {
  const result = PulseEngine.evaluateAlerts({
    alerts: [{ id: "a2", symbol: "HNB.N0000", type: "price_below", target: 225, armed: true, enabled: true }],
    companies: [{ ...baseCompany, symbol: "HNB.N0000", previousClose: 226, price: 224 }],
    now: "2026-07-11T20:00:00.000Z"
  });
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].reason, "threshold_cross_down");
});

run("disclosure alert requires explicit disclosure symbol", () => {
  const noDisclosure = PulseEngine.evaluateAlerts({
    alerts: [{ id: "a3", symbol: "COMB.N0000", type: "disclosure", target: 0, armed: true, enabled: true }],
    companies: [{ ...baseCompany, symbol: "COMB.N0000" }],
    now: "2026-07-11T20:00:00.000Z",
    disclosureSymbols: []
  });
  assert.equal(noDisclosure.events.length, 0);

  const withDisclosure = PulseEngine.evaluateAlerts({
    alerts: [{ id: "a3", symbol: "COMB.N0000", type: "disclosure", target: 0, armed: true, enabled: true }],
    companies: [{ ...baseCompany, symbol: "COMB.N0000" }],
    now: "2026-07-11T20:00:00.000Z",
    disclosureSymbols: ["COMB.N0000"]
  });
  assert.equal(withDisclosure.events.length, 1);
  assert.equal(withDisclosure.events[0].reason, "new_disclosure");
});

run("volume spike evaluates volume change percent", () => {
  const result = PulseEngine.evaluateAlerts({
    alerts: [{ id: "a4", symbol: "DIAL.N0000", type: "volume_spike", target: 40, armed: true, enabled: true }],
    companies: [{ ...baseCompany, symbol: "DIAL.N0000", previousVolume: 1000, volume: 1800 }],
    now: "2026-07-11T20:00:00.000Z"
  });
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].reason, "volume_spike");
});

run("risk score is bounded from 0 to 100", () => {
  const score = PulseEngine.riskScore({ ...baseCompany, history: [10, 12, 9, 13, 8, 15] });
  assert.equal(score >= 0 && score <= 100, true);
});
