# backend/app/services/broadcaster.py
import asyncio
import json
import logging
from typing import Set, AsyncGenerator

logger = logging.getLogger("hrmodule.broadcaster")

class ScoreEventBroadcaster:
    """
    Thread-safe asynchronous broadcasting engine.
    Manages active client network streams safely inside RAM.
    """
    def __init__(self):
        # Keeps track of all active browser connection queues
        self._listeners: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Registers a fresh browser tab connection to the stream."""
        queue = asyncio.Queue()
        async with self._lock:
            self._listeners.add(queue)
        
        logger.info("New dashboard client tuned into real-time stream", extra={"total_listeners": len(self._listeners)})
        
        try:
            while True:
                # Keep listening until the browser breaks the socket connection
                event_data = await queue.get()
                yield event_data
        except asyncio.CancelledError:
            # Caught automatically when a client closes their browser tab
            pass
        finally:
            # Structural Clean-up: Remove the dead queue to guarantee zero memory leaks
            async with self._lock:
                self._listeners.remove(queue)
            logger.info("Client disconnected from stream. RAM cleared.", extra={"total_listeners": len(self._listeners)})

    async def broadcast_score_update(self, candidate_id: int, category: str, score: int, reviewer_name: str):
        """Pushes a fresh evaluation score payload to all connected clients simultaneously."""
        payload = json.dumps({
            "candidate_id": candidate_id,
            "category": category,
            "score": score,
            "reviewer": reviewer_name
        })
        
        # Exact wire protocol format: event line, data line, followed by a double newline
        sse_event = f"event: score_update\ndata: {payload}\n\n"
        
        async with self._lock:
            if not self._listeners:
                return
            # Blast the text row into all active queues concurrently
            await asyncio.gather(*[q.put(sse_event) for q in self._listeners])


# Single global instance accessible across your entire app package
score_broadcaster = ScoreEventBroadcaster()
