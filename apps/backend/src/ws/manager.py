from __future__ import annotations

import logging
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Tracks live WebSocket connections grouped by organization_id.
    Thread-safe within a single asyncio event loop — no external locking needed
    because all mutations happen in the same loop without yielding mid-mutation.
    """

    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    def connect(self, websocket: WebSocket, organization_id: UUID) -> None:
        self._connections[organization_id].add(websocket)
        logger.debug(
            "WebSocket connected.",
            extra={
                "organization_id": str(organization_id),
                "total": len(self._connections[organization_id]),
            },
        )

    def disconnect(self, websocket: WebSocket, organization_id: UUID) -> None:
        connections = self._connections.get(organization_id)
        if connections:
            connections.discard(websocket)
            if not connections:
                del self._connections[organization_id]
        logger.debug("WebSocket disconnected.", extra={"organization_id": str(organization_id)})

    async def broadcast_to_org(self, organization_id: UUID, payload: dict) -> None:
        """Send a JSON payload to every connected client in the given organization."""
        connections = set(self._connections.get(organization_id, set()))
        if not connections:
            return

        stale: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(payload)
            except Exception:
                stale.append(ws)

        for ws in stale:
            self.disconnect(ws, organization_id)

    def active_count(self, organization_id: UUID) -> int:
        return len(self._connections.get(organization_id, set()))


manager = ConnectionManager()
