import asyncio
import logging
from typing import Optional, Tuple

from backend.app.core.config import settings
from backend.app.services.metrics import inc

logger = logging.getLogger(__name__)


class _TrapsProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport: Optional[asyncio.DatagramTransport] = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport
        logger.info("SNMP traps UDP receiver started on %s", transport.get_extra_info("sockname"))

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        try:
            _ = data.decode("utf-8", errors="replace")
            inc("snmp_traps_total", 1)
        except Exception:
            inc("snmp_traps_decode_errors_total", 1)

    def error_received(self, exc: Exception) -> None:
        logger.warning("SNMP traps UDP receiver error: %s", exc)
        inc("snmp_traps_receiver_errors_total", 1)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        logger.info("SNMP traps UDP receiver stopped")


async def run_traps_server(stop_event: asyncio.Event) -> None:
    if not settings.TRAPS_ENABLED:
        return

    loop = asyncio.get_running_loop()
    protocol = _TrapsProtocol()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: protocol,
        local_addr=("0.0.0.0", settings.TRAPS_UDP_PORT),
    )
    try:
        await stop_event.wait()
    finally:
        transport.close()
