# src/tests/test_websocket.py

import pytest
import asyncio
from websockets import connect
from pulse_cse.config import settings

@pytest.mark.asyncio
async def test_websocket_connection():
    async with connect(f"ws://{settings.WEBSOCKET_HOST}:{settings.WEBSOCKET_PORT}") as websocket:
        await websocket.send("ping")
        response = await websocket.recv()
        assert response == "pong"

@pytest.mark.asyncio
async def test_websocket_price_updates():
    async with connect(f"ws://{settings.WEBSOCKET_HOST}:{settings.WEBSOCKET_PORT}") as websocket:
        await websocket.send("subscribe")
        response = await websocket.recv()
        assert response.startswith("price_update")

@pytest.mark.asyncio
async def test_websocket_invalid_message():
    async with connect(f"ws://{settings.WEBSOCKET_HOST}:{settings.WEBSOCKET_PORT}") as websocket:
        await websocket.send("invalid_message")
        response = await websocket.recv()
        assert response == "error: invalid message"

@pytest.mark.asyncio
async def test_websocket_connection_close():
    async with connect(f"ws://{settings.WEBSOCKET_HOST}:{settings.WEBSOCKET_PORT}") as websocket:
        await websocket.send("close")
        with pytest.raises(ConnectionClosed):
            await websocket.recv()