from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from src.core.security import decode_token
from src.db.session import AsyncSessionLocal
from src.repositories import UserRepository
from src.ws.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    Authenticated WebSocket endpoint for real-time notifications.

    Connect with:  ws://<host>/api/v1/ws/notifications?token=<access_token>

    The server pushes JSON messages of the shape:
        {"type": "notification", "id": "...", "title": "...", "message": "...", "created_at": "..."}
    """
    await websocket.accept()

    # Authenticate via JWT query param
    try:
        payload = decode_token(token, expected_token_type="access")
        user_id_str: str | None = payload.get("sub")
        org_id_str: str | None = payload.get("org")
        if not user_id_str or not org_id_str:
            raise ValueError("Missing JWT claims.")
    except Exception:
        logger.warning("WebSocket rejected: invalid token.")
        await websocket.close(code=4001, reason="Unauthorized")
        return

    user_id = UUID(user_id_str)
    org_id = UUID(org_id_str)

    # Verify the user is still active (short-lived session, released immediately)
    async with AsyncSessionLocal() as session:
        user = await UserRepository(session).get_by_id(user_id)

    if user is None or not user.is_active:
        logger.warning("WebSocket rejected: inactive user.", extra={"user_id": str(user_id)})
        await websocket.close(code=4001, reason="Unauthorized")
        return

    manager.connect(websocket, org_id)
    logger.info("WebSocket authenticated.", extra={"user_id": str(user_id), "org_id": str(org_id)})

    try:
        while True:
            # Drain any client messages; we don't process them but keeping the
            # receive loop running is what keeps the connection alive.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("Unexpected WebSocket error.", extra={"user_id": str(user_id)})
    finally:
        manager.disconnect(websocket, org_id)
