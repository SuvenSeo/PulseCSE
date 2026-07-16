import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

from src.core.models import (
    Company,
    Holding,
    Portfolio,
    Alert,
    AlertType,
    AlertStatus,
    AlertSeverity,
    PortfolioDrawdownAlertConfig,
    PortfolioHoldingAlertConfig,
)
from src.core.portfolio import PortfolioService
from src.core.adapters import AbstractMarketDataAdapter
from src.storage.abstract import AbstractStorage


# --- Fixtures for Mock Data and Services ---

@pytest.fixture
def mock_company_jkh():
    return Company(
        symbol="JKH",
        name="John Keells Holdings PLC",
        sector="Diversified Holdings",
        last_price=150.0,
        fifty_two_week_high=170.0,
        fifty_two_week_low=120.0,
        market_cap=200000000000.0,
        pe_ratio=12.5,
        eps=12.0,
        volume=1000000,
        last_updated=datetime.now(),
    )


@pytest.fixture
def mock_company_spen():
    return Company(
        symbol="SPEN",
        name="Sunshine Holdings PLC",
        sector="Healthcare",
        last_price=75.0,
        fifty_two_week_high=80.0,
        fifty_two_week_low=60.0,
        market_cap=50000000000.0,
        pe_ratio=10.0,
        eps=7.5,
        volume=500000,
        last_updated=datetime.now(),
    )


@pytest.fixture
def mock_company_hnb():
    return Company(
        symbol="HNB",
        name="Hatton National Bank",
        sector="Banking",
        last_price=125.0,
        fifty_two_week_high=130.0,
        fifty_two_week_low=100.0,
        market_cap=100000000000.0,
        pe_ratio=8.0,
        eps=15.0,
        volume=750000,
        last_updated=datetime.now(),
    )


@pytest.fixture
def mock_storage():
    return MagicMock(spec=AbstractStorage)


@pytest.fixture
def mock_market_data_adapter(mock_company_jkh, mock_company_spen, mock_company_hnb):
    adapter = MagicMock(spec=AbstractMarketDataAdapter)

    def get_current_price_side_effect(symbol):
        prices = {
            "JKH": mock_company_jkh.last_price,
            "SPEN": mock_company_spen.last_price,
            "HNB": mock_company_hnb.last_price,
        }
        return prices.get(symbol)

    def get_company_info_side_effect(symbol):
        companies = {
            "JKH": mock_company_jkh,
            "SPEN": mock_company_spen,
            "HNB": mock_company_hnb,
        }
        return companies.get(symbol)

    adapter.get_current_price.side_effect = get_current_price_side_effect
    adapter.get_company_info.side_effect = get_company_info_side_effect
    return adapter


@pytest.fixture
def portfolio_service(mock_storage, mock_market_data_adapter):
    return PortfolioService(mock_storage, mock_market_data_adapter)


@pytest.fixture
def sample_portfolio(mock_company_jkh, mock_company_spen):
    portfolio = Portfolio(
        id="test_portfolio_1",
        user_id="test_user",
        name="My Test Portfolio",
        holdings=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        risk_score=None, # Assuming risk_score can be None initially
    )
    portfolio.holdings.append(
        Holding(
            symbol=mock_company_jkh.symbol,
            shares=100,
            buy_price=140.0,
            buy_date=date(2023, 1, 1),
            current_price=mock_company_jkh.last_price,
        )
    )
    portfolio.holdings.append(
        Holding(
            symbol=mock_company_spen.symbol,
            shares=200,
            buy_price=70.0,
            buy_date=date(2023, 2, 1),
            current_price=mock_company_spen.last_price,
        )
    )
    return portfolio


# --- Tests for PortfolioService ---

class TestPortfolioService:

    def test_create_portfolio(self, portfolio_service, mock_storage):
        user_id = "test_user_new"
        name = "New Portfolio"
        portfolio = portfolio_service.create_portfolio(user_id, name)

        assert portfolio.user_id == user_id
        assert portfolio.name == name
        assert len(portfolio.holdings) == 0
        assert portfolio.risk_score is None # Should be None upon creation
        mock_storage.save_portfolio.assert_called_once_with(portfolio)

    def test_get_portfolio(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio
        retrieved_portfolio = portfolio_service.get_portfolio(sample_portfolio.id)

        assert retrieved_portfolio == sample_portfolio
        mock_storage.get_portfolio.assert_called_once_with(sample_portfolio.id)

    def test_get_all_portfolios_for_user(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolios_by_user_id.return_value = [sample_portfolio]
        portfolios = portfolio_service.get_all_portfolios_for_user(sample_portfolio.user_id)

        assert len(portfolios) == 1
        assert portfolios[0] == sample_portfolio
        mock_storage.get_portfolios_by_user_id.assert_called_once_with(sample_portfolio.user_id)

    def test_add_holding_to_portfolio(self, portfolio_service, mock_storage, sample_portfolio, mock_company_hnb):
        mock_storage.get_portfolio.return_value = sample_portfolio
        initial_holdings_count = len(sample_portfolio.holdings)

        new_symbol = mock_company_hnb.symbol
        new_shares = 50
        new_buy_price = 120.0
        new_buy_date = date(2023, 3, 1)

        # Mock current price and company info for the new holding explicitly
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda sym: {
            "JKH": 150.0, "SPEN": 75.0, "HNB": 125.0
        }.get(sym)
        portfolio_service.market_data_adapter.get_company_info.side_effect = lambda sym: {
            "JKH": mock_company_jkh, "SPEN": mock_company_spen, "HNB": mock_company_hnb
        }.get(sym)

        updated_portfolio = portfolio_service.add_holding_to_portfolio(
            sample_portfolio.id, new_symbol, new_shares, new_buy_price, new_buy_date
        )

        assert len(updated_portfolio.holdings) == initial_holdings_count + 1
        added_holding = next(h for h in updated_portfolio.holdings if h.symbol == new_symbol)
        assert added_holding.shares == new_shares
        assert added_holding.buy_price == new_buy_price
        assert added_holding.current_price == mock_company_hnb.last_price
        mock_storage.save_portfolio.assert_called_once_with(updated_portfolio)

    def test_remove_holding_from_portfolio(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio
        initial_holdings_count = len(sample_portfolio.holdings)
        symbol_to_remove = "JKH"

        updated_portfolio = portfolio_service.remove_holding_from_portfolio(sample_portfolio.id, symbol_to_remove)

        assert len(updated_portfolio.holdings) == initial_holdings_count - 1
        assert not any(h.symbol == symbol_to_remove for h in updated_portfolio.holdings)
        mock_storage.save_portfolio.assert_called_once_with(updated_portfolio)

    def test_update_holding_in_portfolio(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio
        symbol_to_update = "JKH"
        new_shares = 150
        new_buy_price = 145.0

        updated_portfolio = portfolio_service.update_holding_in_portfolio(
            sample_portfolio.id, symbol_to_update, new_shares, new_buy_price
        )

        jkh_holding = next(h for h in updated_portfolio.holdings if h.symbol == symbol_to_update)
        assert jkh_holding.shares == new_shares
        assert jkh_holding.buy_price == new_buy_price
        mock_storage.save_portfolio.assert_called_once_with(updated_portfolio)

    def test_calculate_portfolio_pnl(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio

        # JKH: 100 shares * (150 - 140) = 100 * 10 = 1000
        # SPEN: 200 shares * (75 - 70) = 200 * 5 = 1000
        # Total PnL = 2000

        pnl_data = portfolio_service.calculate_portfolio_pnl(sample_portfolio.id)

        assert pnl_data["total_pnl"] == 2000.0
        assert pnl_data["total_invested"] == (100 * 140.0) + (200 * 70.0)
        assert pnl_data["current_value"] == (100 * 150.0) + (200 * 75.0)
        assert pnl_data["pnl_percentage"] == pytest.approx(
            2000.0 / ((100 * 140.0) + (200 * 70.0)) * 100, abs=0.01
        )

    def test_get_portfolio_summary(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio

        summary = portfolio_service.get_portfolio_summary(sample_portfolio.id)

        assert summary["portfolio_id"] == sample_portfolio.id
        assert summary["portfolio_name"] == sample_portfolio.name
        assert summary["num_holdings"] == 2
        assert summary["total_invested"] == (100 * 140.0) + (200 * 70.0)
        assert summary["current_value"] == (100 * 150.0) + (200 * 75.0)
        assert summary["total_pnl"] == 2000.0
        assert summary["pnl_percentage"] == pytest.approx(
            2000.0 / ((100 * 140.0) + (200 * 70.0)) * 100, abs=0.01
        )
        assert isinstance(summary["holdings_summary"], list)
        assert len(summary["holdings_summary"]) == 2
        assert any(h["symbol"] == "JKH" for h in summary["holdings_summary"])
        assert any(h["symbol"] == "SPEN" for h in summary["holdings_summary"])

    @patch("src.core.portfolio._get_historical_peak_value")
    def test_calculate_portfolio_drawdown(self, mock_get_peak, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio
        mock_get_peak.return_value = 32000.0  # Simulate a historical peak value for the portfolio

        # Current value: JKH 100*150 + SPEN 200*75 = 15000 + 15000 = 30000
        # Drawdown = (32000 - 30000) / 32000 = 2000 / 32000 = 0.0625 = 6.25%
        drawdown_percent = portfolio_service.calculate_portfolio_drawdown(sample_portfolio.id)
        assert drawdown_percent == pytest.approx(6.25, abs=0.01)
        mock_get_peak.assert_called_once_with(sample_portfolio.id, portfolio_service.storage)


    @patch("src.core.portfolio._get_historical_peak_value")
    def test_evaluate_portfolio_drawdown_alert_trigger(
        self, mock_get_peak, portfolio_service, mock_storage, sample_portfolio
    ):
        mock_storage.get_portfolio.return_value = sample_portfolio
        mock_storage.get_alerts_for_portfolio.return_value = [] # No existing alerts

        alert_config = PortfolioDrawdownAlertConfig(
            threshold_percent=5.0,
            cooldown_minutes=60,
        )

        mock_get_peak.return_value = 32000.0  # Peak value
        # Adjust current prices to cause a drawdown > 5%
        # Current value 29000 -> (32000 - 29000) / 32000 = 3000 / 32000 = 9.375% drawdown
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 130.0,  # 100 * 130 = 13000
            "SPEN": 80.0,  # 200 * 80 = 16000
        }.get(symbol)

        new_alert = portfolio_service.evaluate_portfolio_drawdown_alert(sample_portfolio.id, alert_config)

        assert new_alert is not None
        assert new_alert.alert_type == AlertType.PORTFOLIO_DRAWDOWN
        assert new_alert.status == AlertStatus.TRIGGERED
        assert new_alert.severity == AlertSeverity.CRITICAL
        assert "drawdown of 9.38%" in new_alert.message
        mock_storage.save_alert.assert_called_once()
        mock_storage.update_alert_status.assert_not_called() # Should be a new alert

    @patch("src.core.portfolio._get_historical_peak_value")
    def test_evaluate_portfolio_drawdown_alert_no_trigger(
        self, mock_get_peak, portfolio_service, mock_storage, sample_portfolio
    ):
        mock_storage.get_portfolio.return_value = sample_portfolio
        mock_storage.get_alerts_for_portfolio.return_value = [] # No existing alerts

        alert_config = PortfolioDrawdownAlertConfig(
            threshold_percent=10.0, # Higher threshold
            cooldown_minutes=60,
        )

        mock_get_peak.return_value = 32000.0
        # Current value 30000 -> (32000 - 30000) / 32000 = 6.25% drawdown (below 10% threshold)
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 150.0,
            "SPEN": 75.0,
        }.get(symbol)

        new_alert = portfolio_service.evaluate_portfolio_drawdown_alert(sample_portfolio.id, alert_config)

        assert new_alert is None
        mock_storage.save_alert.assert_not_called()

    @patch("src.core.portfolio._get_historical_peak_value")
    def test_evaluate_portfolio_drawdown_alert_cooldown(
        self, mock_get_peak, portfolio_service, mock_storage, sample_portfolio
    ):
        mock_storage.get_portfolio.return_value = sample_portfolio

        alert_config = PortfolioDrawdownAlertConfig(
            threshold_percent=5.0,
            cooldown_minutes=60,
        )

        # Simulate an existing triggered alert within cooldown period
        existing_alert = Alert(
            id="alert_1",
            user_id=sample_portfolio.user_id,
            portfolio_id=sample_portfolio.id,
            alert_type=AlertType.PORTFOLIO_DRAWDOWN,
            config=alert_config,
            status=AlertStatus.TRIGGERED,
            severity=AlertSeverity.CRITICAL,
            message="Portfolio drawdown of 9.0%",
            triggered_at=datetime.now() - timedelta(minutes=30), # Triggered 30 mins ago (within 60 min cooldown)
            last_checked_at=datetime.now(),
            company_symbol=None,
        )
        mock_storage.get_alerts_for_portfolio.return_value = [existing_alert]

        mock_get_peak.return_value = 32000.0
        # Current value 29000 -> 9.375% drawdown (still past threshold)
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 130.0,
            "SPEN": 80.0,
        }.get(symbol)

        new_alert = portfolio_service.evaluate_portfolio_drawdown_alert(sample_portfolio.id, alert_config)

        assert new_alert is None # Should not trigger due to cooldown
        mock_storage.save_alert.assert_not_called()
        mock_storage.update_alert_status.assert_not_called()


    @patch("src.core.portfolio._get_historical_peak_value")
    def test_evaluate_portfolio_drawdown_alert_rearm(
        self, mock_get_peak, portfolio_service, mock_storage, sample_portfolio
    ):
        mock_storage.get_portfolio.return_value = sample_portfolio

        alert_config = PortfolioDrawdownAlertConfig(
            threshold_percent=5.0,
            cooldown_minutes=60,
        )

        # Simulate an existing triggered alert that has passed cooldown
        existing_alert = Alert(
            id="alert_1",
            user_id=sample_portfolio.user_id,
            portfolio_id=sample_portfolio.id,
            alert_type=AlertType.PORTFOLIO_DRAWDOWN,
            config=alert_config,
            status=AlertStatus.TRIGGERED,
            severity=AlertSeverity.CRITICAL,
            message="Portfolio drawdown of 9.0%",
            triggered_at=datetime.now() - timedelta(hours=2), # Triggered 2 hours ago (past cooldown)
            last_checked_at=datetime.now(),
            company_symbol=None,
        )
        mock_storage.get_alerts_for_portfolio.return_value = [existing_alert]

        mock_get_peak.return_value = 32000.0
        # Current value 29000 -> 9.375% drawdown (still past threshold)
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 130.0,
            "SPEN": 80.0,
        }.get(symbol)

        new_alert = portfolio_service.evaluate_portfolio_drawdown_alert(sample_portfolio.id, alert_config)

        assert new_alert is not None
        assert new_alert.alert_type == AlertType.PORTFOLIO_DRAWDOWN
        assert new_alert.status == AlertStatus.TRIGGERED
        assert new_alert.id != existing_alert.id # Should be a new alert if re-armed
        mock_storage.save_alert.assert_called_once_with(new_alert)
        # The old alert should be resolved if a new one is triggered after cooldown
        mock_storage.update_alert_status.assert_called_once_with(existing_alert.id, AlertStatus.RESOLVED)

    @patch("src.core.portfolio.calculate_risk_score_for_portfolio")
    def test_update_portfolio_risk_score(
        self, mock_calculate_risk, portfolio_service, mock_storage, sample_portfolio
    ):
        mock_storage.get_portfolio.return_value = sample_portfolio
        mock_calculate_risk.return_value = 0.75 # Example risk score

        updated_portfolio = portfolio_service.update_portfolio_risk_score(sample_portfolio.id)

        assert updated_portfolio.risk_score == 0.75
        mock_storage.save_portfolio.assert_called_once_with(updated_portfolio)
        mock_calculate_risk.assert_called_once_with(sample_portfolio)

    def test_evaluate_holding_price_alert_trigger(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio
        mock_storage.get_active_alerts_for_holding.return_value = []

        holding_alert_config = PortfolioHoldingAlertConfig(
            symbol="JKH",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=155.0, # Current price is 150.0, but we'll mock it higher
            cooldown_minutes=60,
        )

        # Mock JKH price to trigger the alert
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 160.0,
            "SPEN": 75.0,
        }.get(symbol)

        new_alert = portfolio_service.evaluate_holding_alert(sample_portfolio.id, holding_alert_config)

        assert new_alert is not None
        assert new_alert.alert_type == AlertType.PRICE_ABOVE
        assert new_alert.status == AlertStatus.TRIGGERED
        assert new_alert.company_symbol == "JKH"
        assert "JKH price 160.0 is above threshold 155.0" in new_alert.message
        mock_storage.save_alert.assert_called_once()
        mock_storage.update_alert_status.assert_not_called()

    def test_evaluate_holding_price_alert_no_trigger(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio
        mock_storage.get_active_alerts_for_holding.return_value = []

        holding_alert_config = PortfolioHoldingAlertConfig(
            symbol="JKH",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=160.0, # Current price is 150.0
            cooldown_minutes=60,
        )

        # JKH price remains 150.0, below threshold
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 150.0,
            "SPEN": 75.0,
        }.get(symbol)

        new_alert = portfolio_service.evaluate_holding_alert(sample_portfolio.id, holding_alert_config)

        assert new_alert is None
        mock_storage.save_alert.assert_not_called()

    def test_evaluate_holding_price_alert_cooldown(self, portfolio_service, mock_storage, sample_portfolio):
        mock_storage.get_portfolio.return_value = sample_portfolio

        holding_alert_config = PortfolioHoldingAlertConfig(
            symbol="JKH",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=155.0,
            cooldown_minutes=60,
        )

        existing_alert = Alert(
            id="alert_jkh_1",
            user_id=sample_portfolio.user_id,
            portfolio_id=sample_portfolio.id,
            alert_type=AlertType.PRICE_ABOVE,
            config=holding_alert_config,
            status=AlertStatus.TRIGGERED,
            severity=AlertSeverity.INFO,
            message="JKH price 160.0 is above threshold 155.0",
            triggered_at=datetime.now() - timedelta(minutes=30), # Within cooldown
            last_checked_at=datetime.now(),
            company_symbol="JKH",
        )
        mock_storage.get_active_alerts_for_holding.return_value = [existing_alert]

        # JKH price is still above threshold
        portfolio_service.market_data_adapter.get_current_price.side_effect = lambda symbol: {
            "JKH": 160.0,
            "SPEN": 75.0,
        }.get(symbol)

        new_alert = portfolio_service.evaluate_holding_alert(sample_portfolio.id, holding_alert_config)

        assert new_alert is None
        mock_storage.save_alert.assert_not_called()
        mock_storage.update_alert_status.assert_not_called()