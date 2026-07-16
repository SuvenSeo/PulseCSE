"""
Main entry point for the PulseCSE application.
"""

import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import routes
from core import settings
from core.engine import AlertEngine
from core.models import AlertType
from core.storage import Database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# Initialize the FastAPI app
app = FastAPI(
    title="PulseCSE",
    description="A full-stack investor cockpit for the CSE.",
    version="1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(routes.api_router)

# Initialize the alert engine
alert_engine = AlertEngine()

# Initialize the database
database = Database()

# Load settings from environment variables
settings.load_env()

# Define a function to run the alert engine
def run_alert_engine():
    """
    Run the alert engine to process alerts.
    """
    alert_engine.run()

# Define a function to seed the database
def seed_database():
    """
    Seed the database with initial data.
    """
    database.seed()

# Define a function to migrate the database
def migrate_database():
    """
    Migrate the database to the latest version.
    """
    database.migrate()

# Define a function to simulate alerts
def simulate_alerts():
    """
    Simulate alerts for testing purposes.
    """
    alert_engine.simulate()

# Define a function to run the application
def run_app():
    """
    Run the PulseCSE application.
    """
    # Run the alert engine
    run_alert_engine()

    # Seed the database
    seed_database()

    # Migrate the database
    migrate_database()

    # Simulate alerts
    simulate_alerts()

# Run the application
if __name__ == "__main__":
    run_app()

    # Start the FastAPI app
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)