import asyncio
import logging
from typing import Optional, Tuple

from backend.app.core.config import settings
from backend.app.services.metrics import inc

logger = logging.getLogger(__name__)


class _SyslogProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport: Optional[asyncio.DatagramTransport] = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport
        logger.info("Syslog UDP receiver started on %s", transport.get_extra_info("sockname"))

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        try:
            _ = data.decode("utf-8", errors="replace")
            inc("syslog_messages_total", 1)
        except Exception:
            inc("syslog_messages_decode_errors_total", 1)

    def error_received(self, exc: Exception) -> None:
        logger.warning("Syslog UDP receiver error: %s", exc)
        inc("syslog_receiver_errors_total", 1)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        logger.info("Syslog UDP receiver stopped")


async def run_syslog_server(stop_event: asyncio.Event) -> None:
    if not settings.SYSLOG_ENABLED:
        return

    loop = asyncio.get_running_loop()
    protocol = _SyslogProtocol()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: protocol,
        local_addr=("0.0.0.0", settings.SYSLOG_UDP_PORT),
    )
    try:
        await stop_event.wait()
    finally:
        transport.close()
