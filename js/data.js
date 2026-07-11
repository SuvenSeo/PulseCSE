const PulseData = (() => {
  const companies = [
    {
      symbol: "JKH.N0000",
      name: "John Keells Holdings PLC",
      sector: "Capital Goods",
      price: 191.25,
      previousClose: 186.1,
      volume: 1284000,
      previousVolume: 1016000,
      marketCap: "LKR 265.2B",
      description: "Diversified blue-chip group with exposure to leisure, transport, retail, property, and financial services.",
      history: [171.2, 174.1, 176.4, 178.8, 180.3, 184.2, 186.1, 191.25],
      disclosure: "Board update and quarterly performance briefing released.",
      signal: "Momentum"
    },
    {
      symbol: "COMB.N0000",
      name: "Commercial Bank of Ceylon PLC",
      sector: "Banks",
      price: 104.8,
      previousClose: 102.9,
      volume: 734000,
      previousVolume: 702000,
      marketCap: "LKR 122.8B",
      description: "Large private commercial bank with retail, corporate, SME, and digital banking operations.",
      history: [98.7, 99.5, 100.1, 101.4, 101.9, 102.4, 102.9, 104.8],
      disclosure: "Interim financial statement uploaded for shareholder review.",
      signal: "Quality"
    },
    {
      symbol: "HNB.N0000",
      name: "Hatton National Bank PLC",
      sector: "Banks",
      price: 224.4,
      previousClose: 226.5,
      volume: 312000,
      previousVolume: 349000,
      marketCap: "LKR 118.6B",
      description: "Systemically important bank serving corporate, retail, SME, and development banking markets.",
      history: [218.2, 219.9, 221.4, 223.8, 225.9, 227.2, 226.5, 224.4],
      disclosure: "Credit rating surveillance update announced.",
      signal: "Pullback"
    },
    {
      symbol: "DIAL.N0000",
      name: "Dialog Axiata PLC",
      sector: "Telecommunication Services",
      price: 12.9,
      previousClose: 12.55,
      volume: 4372000,
      previousVolume: 3880000,
      marketCap: "LKR 106.4B",
      description: "Telecommunications operator providing mobile, fixed broadband, TV, and enterprise connectivity solutions.",
      history: [11.7, 11.9, 12.1, 12.2, 12.35, 12.4, 12.55, 12.9],
      disclosure: "Network investment update and investor presentation posted.",
      signal: "Volume"
    },
    {
      symbol: "LOLC.N0000",
      name: "LOLC Holdings PLC",
      sector: "Diversified Financials",
      price: 428.75,
      previousClose: 421.0,
      volume: 216000,
      previousVolume: 182000,
      marketCap: "LKR 203.5B",
      description: "Diversified financial group with leasing, microfinance, insurance, plantations, leisure, and overseas operations.",
      history: [398.0, 402.5, 407.2, 411.8, 416.4, 419.2, 421.0, 428.75],
      disclosure: "Subsidiary transaction update disclosed to market.",
      signal: "Breakout"
    },
    {
      symbol: "HAYL.N0000",
      name: "Hayleys PLC",
      sector: "Capital Goods",
      price: 91.2,
      previousClose: 89.8,
      volume: 497000,
      previousVolume: 441000,
      marketCap: "LKR 68.4B",
      description: "Conglomerate active in export manufacturing, agriculture, logistics, power, consumer, and leisure sectors.",
      history: [84.1, 85.7, 87.0, 87.8, 88.4, 89.2, 89.8, 91.2],
      disclosure: "Annual report notice and AGM schedule released.",
      signal: "Accumulation"
    },
    {
      symbol: "CTC.N0000",
      name: "Ceylon Tobacco Company PLC",
      sector: "Food Beverage and Tobacco",
      price: 1420.0,
      previousClose: 1435.5,
      volume: 4800,
      previousVolume: 5200,
      marketCap: "LKR 266.1B",
      description: "Consumer staples company with defensive cash-flow characteristics and high dividend attention.",
      history: [1392, 1401, 1410, 1418, 1429, 1440, 1435.5, 1420],
      disclosure: "Dividend announcement reminder and shareholder circular posted.",
      signal: "Defensive"
    },
    {
      symbol: "EXPO.N0000",
      name: "Expolanka Holdings PLC",
      sector: "Transportation",
      price: 153.0,
      previousClose: 150.25,
      volume: 887000,
      previousVolume: 802000,
      marketCap: "LKR 299.1B",
      description: "Logistics group with freight forwarding, supply-chain, and regional trade exposure.",
      history: [145.2, 146.4, 147.8, 149.0, 149.5, 150.0, 150.25, 153.0],
      disclosure: "Logistics segment performance commentary published.",
      signal: "Recovery"
    },
    {
      symbol: "SAMP.N0000",
      name: "Sampath Bank PLC",
      sector: "Banks",
      price: 82.65,
      previousClose: 83.1,
      volume: 612000,
      previousVolume: 664000,
      marketCap: "LKR 96.3B",
      description: "Commercial bank known for digital services, consumer banking, corporate banking, and remittance products.",
      history: [79.8, 80.4, 81.2, 82.6, 83.0, 83.4, 83.1, 82.65],
      disclosure: "Capital adequacy update included in interim statement.",
      signal: "Range"
    },
    {
      symbol: "NDB.N0000",
      name: "National Development Bank PLC",
      sector: "Banks",
      price: 72.1,
      previousClose: 70.9,
      volume: 224000,
      previousVolume: 205000,
      marketCap: "LKR 32.4B",
      description: "Banking group with development finance history and integrated investment banking services.",
      history: [66.0, 67.8, 68.9, 69.8, 70.4, 70.7, 70.9, 72.1],
      disclosure: "Investor presentation and branch network update filed.",
      signal: "Early strength"
    },
    {
      symbol: "AEL.N0000",
      name: "Access Engineering PLC",
      sector: "Capital Goods",
      price: 27.4,
      previousClose: 27.85,
      volume: 349000,
      previousVolume: 372000,
      marketCap: "LKR 27.4B",
      description: "Construction and engineering group with infrastructure, property, and related material operations.",
      history: [28.6, 28.4, 28.1, 27.9, 27.7, 27.8, 27.85, 27.4],
      disclosure: "Project award notification and corporate disclosure posted.",
      signal: "Watch support"
    },
    {
      symbol: "DIST.N0000",
      name: "Distilleries Company of Sri Lanka PLC",
      sector: "Food Beverage and Tobacco",
      price: 32.75,
      previousClose: 31.9,
      volume: 958000,
      previousVolume: 790000,
      marketCap: "LKR 98.2B",
      description: "Consumer group with beverage, manufacturing, and investment holdings exposure.",
      history: [29.7, 30.2, 30.8, 31.0, 31.35, 31.7, 31.9, 32.75],
      disclosure: "Quarterly earnings and dividend discussion released.",
      signal: "Income"
    }
  ];

  const defaultWatchlist = ["JKH.N0000", "COMB.N0000", "DIAL.N0000", "LOLC.N0000", "HAYL.N0000"];

  const sampleAlerts = [
    {
      id: "alert-jkh-above",
      symbol: "JKH.N0000",
      type: "price_above",
      target: 195,
      note: "Breakout watch",
      enabled: true,
      armed: true,
      cooldownMinutes: 30,
      fireCount: 0,
      createdAt: new Date().toISOString()
    },
    {
      id: "alert-comb-disclosure",
      symbol: "COMB.N0000",
      type: "disclosure",
      target: 0,
      note: "Bank disclosure update",
      enabled: true,
      armed: true,
      cooldownMinutes: 30,
      fireCount: 0,
      createdAt: new Date().toISOString()
    },
    {
      id: "alert-hnb-below",
      symbol: "HNB.N0000",
      type: "price_below",
      target: 220,
      note: "Risk check",
      enabled: true,
      armed: true,
      cooldownMinutes: 30,
      fireCount: 0,
      createdAt: new Date().toISOString()
    },
    {
      id: "alert-dial-move",
      symbol: "DIAL.N0000",
      type: "percent_move",
      target: 3.5,
      note: "Momentum spike",
      enabled: true,
      armed: true,
      cooldownMinutes: 30,
      fireCount: 0,
      createdAt: new Date().toISOString()
    },
    {
      id: "alert-dial-volume",
      symbol: "DIAL.N0000",
      type: "volume_spike",
      target: 40,
      note: "Unusual volume watch",
      enabled: true,
      armed: true,
      cooldownMinutes: 30,
      fireCount: 0,
      createdAt: new Date().toISOString()
    }
  ];

  return { companies, defaultWatchlist, sampleAlerts };
})();
