import asyncio
import json
import random
import uuid

import websockets

PLAYERS = {}


async def player_handler(websocket):
    """
    Handles player connections, receives player data, and updates other players.
    """
    player_id = str(uuid.uuid4())  # Generate a unique player ID using UUID

    try:
        player_color = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
        await websocket.send(json.dumps({"type": "assigned", "id": player_id, "color": player_color}))

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            # Store player's position and color in the PLAYERS dictionary
            PLAYERS[player_id] = {"x": data.get("x", 0), "y": data.get("y", 0), "color": player_color}, websocket

            await notify_players()

    except websockets.ConnectionClosedOK:
        if player_id in PLAYERS:
            del PLAYERS[player_id]
            await notify_players()


async def notify_players():
    """
    Notifies all players about the current state of the game, including player positions and colors.
    """
    if PLAYERS:
        message = json.dumps(
            {"type": "update", "players": {player_id: player[0] for player_id, player in PLAYERS.items()}}
        )
        await asyncio.gather(*[player[1].send(message) for player in PLAYERS.values()])


async def main():
    """
    Main function to run the WebSocket server.
    """
    async with websockets.serve(player_handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
