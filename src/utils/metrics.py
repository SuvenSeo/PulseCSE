import time
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_client.core import REGISTRY, CollectorRegistry, GaugeMetricFamily
from typing import Optional, Dict

# --- General Application Metrics ---
APP_START_TIME = time.time()

up = Gauge(
    "pulse_app_up", "PulseCSE application is up and running.", labelnames=["version"]
)
app_info = Gauge(
    "pulse_app_info",
    "A gauge with a constant '1' value labeled by version, commit, and build date.",
    labelnames=["version", "commit", "build_date"],
)

# --- API Metrics ---
api_requests_total = Counter(
    "pulse_api_requests_total",
    "Total number of API requests.",
    labelnames=["endpoint", "method", "status_code"],
)
api_request_duration_seconds = Histogram(
    "pulse_api_request_duration_seconds",
    "Histogram of API request durations.",
    labelnames=["endpoint", "method", "status_code"],
)

# --- Alert Engine Metrics ---
alerts_triggered_total = Counter(
    "pulse_alerts_triggered_total",
    "Total number of alerts triggered by the engine.",
    labelnames=["alert_type", "company_symbol", "severity"],
)
alerts_suppressed_total = Counter(
    "pulse_alerts_suppressed_total",
    "Total number of alerts suppressed due to cooldown or fingerprinting.",
    labelnames=["reason", "alert_type"],
)
alert_engine_processing_seconds = Histogram(
    "pulse_alert_engine_processing_seconds",
    "Histogram of alert engine processing durations.",
)
active_alerts_gauge = Gauge(
    "pulse_active_alerts",
    "Current number of active (non-resolved) alerts.",
    labelnames=["alert_type", "severity"],
)

# --- Notification Metrics ---
notifications_sent_total = Counter(
    "pulse_notifications_sent_total",
    "Total number of notifications attempted to be sent.",
    labelnames=["channel", "status"],  # status: 'success', 'failure', 'skipped'
)
notification_delivery_latency_seconds = Histogram(
    "pulse_notification_delivery_latency_seconds",
    "Histogram of notification delivery latencies.",
    labelnames=["channel", "status"],
)
notifications_dead_letter_total = Counter(
    "pulse_notifications_dead_letter_total",
    "Total number of notifications moved to dead-letter queue.",
    labelnames=["channel", "reason"],
)

# --- Poller Metrics ---
poller_runs_total = Counter(
    "pulse_poller_runs_total",
    "Total number of poller runs completed.",
    labelnames=["status"],  # status: 'success', 'failure'
)
poller_run_duration_seconds = Histogram(
    "pulse_poller_run_duration_seconds", "Histogram of poller run durations."
)
data_points_processed_total = Counter(
    "pulse_data_points_processed_total",
    "Total number of data points processed by the poller.",
    labelnames=["adapter_name", "data_type"],
)
market_hours_active = Gauge(
    "pulse_market_hours_active", "Indicates if the market is currently active (1) or not (0)."
)

# --- Storage Metrics ---
db_query_duration_seconds = Histogram(
    "pulse_db_query_duration_seconds",
    "Histogram of database query durations.",
    labelnames=["operation", "table"],
)


class CustomMetricsCollector:
    """
    A custom collector for specific metrics not easily covered by standard clients,
    or for exposing dynamic application state.
    """

    def collect(self):
        # Example: Uptime metric
        uptime_seconds = time.time() - APP_START_TIME
        uptime_metric = GaugeMetricFamily(
            "pulse_app_uptime_seconds",
            "Uptime of the PulseCSE application in seconds.",
            labels=["component"],
        )
        uptime_metric.add_metric(["app"], uptime_seconds)
        yield uptime_metric

        # Add other custom metrics here if needed
        # For example, dynamically count users, active sessions, etc.
        # For now, just uptime.


# Register custom collector with the default registry
REGISTRY.register(CustomMetricsCollector())


def get_metrics_content() -> bytes:
    """Generates the latest Prometheus metrics content."""
    return generate_latest()


def set_app_info(version: str, commit: str, build_date: str):
    """Sets application info metrics."""
    app_info.labels(version=version, commit=commit, build_date=build_date).set(1)
    up.labels(version=version).set(1) # Mark app as up with version


# Example usage (can be called from FastAPI startup event or similar)
# from src.core.config import settings
# set_app_info(settings.APP_VERSION, settings.COMMIT_HASH, settings.BUILD_DATE)

# To expose metrics in FastAPI:
# from fastapi import APIRouter, Response
# metrics_router = APIRouter()
# @metrics_router.get("/metrics", summary="Prometheus metrics endpoint")
# async def prometheus_metrics():
#     return Response(content=get_metrics_content(), media_type=CONTENT_TYPE_LATEST)