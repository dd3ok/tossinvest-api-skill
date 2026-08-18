#!/usr/bin/env python3
"""Stream normalized public TossInvest market updates over STOMP/WebSocket."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import tossinvest_api as api

PUBLIC_ORIGIN = "https://www.tossinvest.com"
GUEST_KEY_URL = "https://wts-api.tossinvest.com/api/v1/refresh-utk"
SOCKET_HOST = "realtime-socket.tossinvest.com"
SOCKET_URL = f"wss://{SOCKET_HOST}/ws"
SUBPROTOCOL = "v12.stomp"
HEARTBEAT_MS = 5_000
CONNECT_TIMEOUT_SECONDS = 10
RECEIVE_TIMEOUT_SECONDS = 1
DISCONNECT_RECEIPT_TIMEOUT_SECONDS = 1
MAX_SUBSCRIPTIONS = 100
MAX_DURATION_SECONDS = 300
MAX_EVENTS = 1_000
MAX_STOMP_FRAME_BYTES = 256 * 1024
MAX_STOMP_CHUNK_BYTES = 1024 * 1024
SUBSCRIPTION_BATCH_SIZE = 20
SUBSCRIPTION_BATCH_INTERVAL_SECONDS = 0.4
OUTPUT_FLUSH_EVENTS = 20
OUTPUT_FLUSH_INTERVAL_SECONDS = 0.5
PROCESS_LOCK_PATH = Path(tempfile.gettempdir()) / "tossinvest-websocket-prices.lock"

_PUBLIC_CODE = re.compile(r"^[A-Za-z0-9._-]{2,48}$")
_KR_STOCK_CODE = re.compile(r"^A[A-Z0-9]{6}$")
_US_STOCK_CODE = re.compile(r"^(?:US|NAS|NYS|AMX)[A-Z0-9._-]{5,45}$")
_CRYPTO_CODE = re.compile(r"^VWAP\.[A-Z0-9._-]{2,40}$")
_HEADER_ESCAPE = re.compile(r"\\([\\cnr])")

_PUBLIC_KR_INDICES = frozenset({"KGG01P", "QGG01P"})
_PUBLIC_US_INDICES = frozenset({"COMP.NAI", "SPX.CBI", "RGI..VIX", "SOX.NAI"})
_PUBLIC_CRYPTO_CODES = frozenset({"VWAP.KRW-BTC", "VWAP.KRW-ETH", "VWAP.KRW-SOL", "VWAP.KRW-XRP"})

_PAYLOAD_FIELDS = (
    "code",
    "exchange",
    "currency",
    "changeType",
    "base",
    "baseKrw",
    "close",
    "closeKrw",
    "open",
    "openKrw",
    "high",
    "highKrw",
    "low",
    "lowKrw",
    "high52w",
    "low52w",
    "high1y",
    "low1y",
    "volume",
    "cumulativeVolume",
    "cumulativeAmount",
    "cumulativeAmountKrw",
    "dt",
    "tradeType",
    "session",
    "tradingStrength",
)


@dataclass(frozen=True)
class Subscription:
    kind: str
    code: str
    destination: str


@dataclass(frozen=True)
class StompFrame:
    command: str
    headers: dict[str, str]
    body: str


class StompParser:
    """Incrementally parse the small STOMP frame subset used by this client."""

    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, chunk: str | bytes) -> list[StompFrame]:
        if isinstance(chunk, bytes):
            chunk_size = len(chunk)
            chunk = chunk.decode("utf-8")
        else:
            chunk_size = len(chunk.encode("utf-8"))
        if chunk_size > MAX_STOMP_CHUNK_BYTES:
            self._buffer = ""
            raise RuntimeError(
                f"WebSocket message exceeded {MAX_STOMP_CHUNK_BYTES} bytes; connection aborted"
            )
        self._buffer += chunk
        frames: list[StompFrame] = []
        while "\x00" in self._buffer:
            raw, self._buffer = self._buffer.split("\x00", 1)
            self._require_frame_size(raw)
            raw = raw.lstrip("\r\n")
            if raw:
                frames.append(parse_stomp_frame(raw))
        self._require_frame_size(self._buffer)
        return frames

    def _require_frame_size(self, value: str) -> None:
        if len(value.encode("utf-8")) <= MAX_STOMP_FRAME_BYTES:
            return
        self._buffer = ""
        raise RuntimeError(
            f"STOMP frame exceeded {MAX_STOMP_FRAME_BYTES} bytes; connection aborted"
        )


class SingleInstanceLock:
    """Keep the standalone client to one connection per local user."""

    def __init__(self, path: Path = PROCESS_LOCK_PATH) -> None:
        self.path = path
        self._handle: Any | None = None

    def __enter__(self) -> SingleInstanceLock:
        descriptor: int | None = None
        try:
            flags = os.O_RDWR | os.O_CREAT
            flags |= getattr(os, "O_BINARY", 0)
            flags |= getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(self.path, flags, 0o600)
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise OSError("lock path is not a regular file")
            if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
                raise OSError("lock file is owned by another user")
            if hasattr(os, "fchmod"):
                os.fchmod(descriptor, 0o600)
            self._handle = os.fdopen(descriptor, "r+b", buffering=0)
            descriptor = None
            if os.name == "nt":
                import msvcrt

                self._handle.seek(0, os.SEEK_END)
                if self._handle.tell() == 0:
                    self._handle.write(b"\x00")
                    self._handle.flush()
                self._handle.seek(0)
                msvcrt.locking(self._handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if descriptor is not None:
                os.close(descriptor)
            if self._handle is not None:
                self._handle.close()
            self._handle = None
            raise RuntimeError(
                "Another TossInvest WebSocket client is already running; reuse or stop it first"
            ) from exc
        return self

    def __exit__(self, *_: Any) -> None:
        if self._handle is None:
            return
        try:
            try:
                if os.name == "nt":
                    import msvcrt

                    self._handle.seek(0)
                    msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        finally:
            self._handle.close()
            self._handle = None


class JsonlEmitter:
    """Flush the first event immediately and batch subsequent writes."""

    def __init__(self, output: Any) -> None:
        self.output = output
        self._pending = 0
        self._last_flush = 0.0

    def __call__(self, event: dict[str, Any]) -> None:
        self.output.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._pending += 1
        now = time.monotonic()
        if (
            self._pending >= OUTPUT_FLUSH_EVENTS
            or now - self._last_flush >= OUTPUT_FLUSH_INTERVAL_SECONDS
        ):
            self.flush(now)

    def flush(self, now: float | None = None) -> None:
        self.output.flush()
        self._pending = 0
        self._last_flush = time.monotonic() if now is None else now


def parse_stomp_frame(raw: str) -> StompFrame:
    normalized = raw.replace("\r\n", "\n")
    head, separator, body = normalized.partition("\n\n")
    if not separator:
        raise RuntimeError("Malformed STOMP frame: missing header/body separator")
    lines = head.split("\n")
    command = lines[0].strip()
    if not command:
        raise RuntimeError("Malformed STOMP frame: missing command")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        key, separator, value = line.partition(":")
        if not separator:
            raise RuntimeError("Malformed STOMP frame: invalid header")
        headers[_unescape_header(key)] = _unescape_header(value)
    return StompFrame(command=command, headers=headers, body=body)


def build_stomp_frame(command: str, headers: dict[str, str], body: str = "") -> str:
    lines = [command]
    for key, value in headers.items():
        if "\r" in key or "\n" in key or "\r" in value or "\n" in value:
            raise ValueError("STOMP headers must not contain line breaks")
        lines.append(f"{key}:{value}")
    return "\n".join([*lines, "", body]) + "\x00"


def build_subscriptions(
    *,
    kr_stocks: Iterable[str] = (),
    us_stocks: Iterable[str] = (),
    kr_indices: Iterable[str] = (),
    us_indices: Iterable[str] = (),
    crypto: Iterable[str] = (),
) -> list[Subscription]:
    requested = [
        *(_subscription_for("kr-stock", code) for code in kr_stocks),
        *(_subscription_for("us-stock", code) for code in us_stocks),
        *(_subscription_for("kr-index", code) for code in kr_indices),
        *(_subscription_for("us-index", code) for code in us_indices),
        *(_subscription_for("crypto", code) for code in crypto),
    ]

    deduplicated = list({item.destination: item for item in requested}.values())
    if not deduplicated:
        raise ValueError("At least one public market code is required")
    if len(deduplicated) > MAX_SUBSCRIPTIONS:
        raise ValueError(f"subscriptions must be at most {MAX_SUBSCRIPTIONS}")
    return deduplicated


def validate_subscriptions(subscriptions: Iterable[Subscription]) -> list[Subscription]:
    validated: list[Subscription] = []
    destinations: set[str] = set()
    for item in subscriptions:
        if not isinstance(item, Subscription):
            raise ValueError("subscriptions must contain Subscription objects")
        canonical = _subscription_for(item.kind, item.code)
        if item != canonical:
            raise ValueError(f"Unsupported or non-canonical destination: {item.destination}")
        if item.destination in destinations:
            raise ValueError(f"Duplicate subscription destination: {item.destination}")
        destinations.add(item.destination)
        validated.append(item)
    if not validated or len(validated) > MAX_SUBSCRIPTIONS:
        raise ValueError(f"subscriptions must contain 1 to {MAX_SUBSCRIPTIONS} destinations")
    return validated


def _subscription_for(kind: str, code: str) -> Subscription:
    if kind == "kr-stock":
        normalized = api.normalize_product_code(code)
        _require_code(normalized, _KR_STOCK_CODE, "KR stock")
        destination = f"/topic/v1/kr/stock/trade/{normalized}"
    elif kind == "us-stock":
        normalized = code.strip().upper()
        _require_code(normalized, _US_STOCK_CODE, "US stock product")
        destination = f"/topic/v1/us/stock/trade/{normalized}"
    elif kind == "kr-index":
        normalized = code.strip()
        _require_code(normalized, _PUBLIC_CODE, "KR index")
        _require_public_index(normalized, _PUBLIC_KR_INDICES, "KR")
        destination = f"/topic/v1/kr/stock/index/{normalized}"
    elif kind == "us-index":
        normalized = code.strip()
        _require_code(normalized, _PUBLIC_CODE, "US index")
        _require_public_index(normalized, _PUBLIC_US_INDICES, "US")
        destination = f"/topic/v1/us/stock/index/{normalized}"
    elif kind == "crypto":
        normalized = code.strip().upper()
        _require_code(normalized, _CRYPTO_CODE, "crypto VWAP")
        _require_public_code(normalized, _PUBLIC_CRYPTO_CODES, "crypto VWAP")
        destination = f"/topic/v1/crypto/vwap/{normalized}"
    else:
        raise ValueError(f"Unsupported subscription kind: {kind}")
    return Subscription(kind, normalized, destination)


def fetch_guest_key(timeout: int = CONNECT_TIMEOUT_SECONDS) -> str:
    request = urllib.request.Request(
        GUEST_KEY_URL,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": PUBLIC_ORIGIN,
            "Referer": f"{PUBLIC_ORIGIN}/",
            "User-Agent": "Mozilla/5.0 tossinvest-api-skill/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read(4_097).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"TossInvest guest bootstrap returned HTTP {exc.code}; stop and reverify the public page"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("TossInvest guest bootstrap failed; reverify the public page") from exc
    key = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(key, str) or not key:
        raise RuntimeError("Unexpected TossInvest guest bootstrap response")
    return key


def normalize_message(subscription: Subscription, payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    event: dict[str, Any] = {
        "kind": subscription.kind,
        "destination": subscription.destination,
    }
    for field in _PAYLOAD_FIELDS:
        value = payload.get(field)
        if isinstance(value, (str, int, float, bool)) or value is None and field in payload:
            event[field] = value
    return event


def stream_prices(
    subscriptions: list[Subscription],
    *,
    duration: int,
    max_events: int,
    emit: Callable[[dict[str, Any]], None],
    guest_key_fetcher: Callable[[], str] = fetch_guest_key,
    websocket_module: Any | None = None,
) -> int:
    duration = api.require_int_range("duration", duration, minimum=1, maximum=MAX_DURATION_SECONDS)
    max_events = api.require_int_range("max-events", max_events, minimum=1, maximum=MAX_EVENTS)
    subscriptions = validate_subscriptions(subscriptions)
    with SingleInstanceLock():
        return _stream_prices_locked(
            subscriptions,
            duration=duration,
            max_events=max_events,
            emit=emit,
            guest_key_fetcher=guest_key_fetcher,
            websocket_module=websocket_module,
        )


def _stream_prices_locked(
    subscriptions: list[Subscription],
    *,
    duration: int,
    max_events: int,
    emit: Callable[[dict[str, Any]], None],
    guest_key_fetcher: Callable[[], str],
    websocket_module: Any | None,
) -> int:

    websocket_module = websocket_module or _load_websocket_module()
    guest_key = guest_key_fetcher()
    device_id = f"WTS-{uuid.uuid4().hex}"
    connection_id = str(uuid.uuid4())
    try:
        socket = websocket_module.create_connection(
            SOCKET_URL,
            subprotocols=[SUBPROTOCOL],
            origin=PUBLIC_ORIGIN,
            timeout=CONNECT_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        raise RuntimeError("TossInvest WebSocket connection failed; stop and reverify") from exc
    socket.settimeout(RECEIVE_TIMEOUT_SECONDS)
    parser = StompParser()
    subscription_by_destination = {item.destination: item for item in subscriptions}
    subscription_ids = {
        item.destination: f"sub-{index}" for index, item in enumerate(subscriptions)
    }
    subscription_by_id = {subscription_ids[item.destination]: item for item in subscriptions}
    emitted = 0
    last_outbound = time.monotonic()
    connected = False
    subscribed_ids: list[str] = []

    try:
        connect_frame = build_stomp_frame(
            "CONNECT",
            {
                "accept-version": "1.2",
                "host": SOCKET_HOST,
                "heart-beat": f"{HEARTBEAT_MS},{HEARTBEAT_MS}",
                "device-id": device_id,
                "connection-id": connection_id,
                "authorization": guest_key,
                "platform": "Web/wts",
            },
        )
        socket.send(connect_frame)
        connect_frame = guest_key = device_id = connection_id = ""
        _wait_until_connected(socket, parser, websocket_module)
        connected = True
        _send_subscriptions(socket, subscriptions, subscription_ids, subscribed_ids)
        last_outbound = time.monotonic()
        deadline = time.monotonic() + duration

        while emitted < max_events and time.monotonic() < deadline:
            if time.monotonic() - last_outbound >= HEARTBEAT_MS / 1_000:
                socket.send("\n")
                last_outbound = time.monotonic()
            try:
                chunk = socket.recv()
            except websocket_module.WebSocketTimeoutException:
                continue
            except getattr(websocket_module, "WebSocketConnectionClosedException", ()) as exc:
                raise RuntimeError(
                    "TossInvest WebSocket closed unexpectedly; stop and reverify"
                ) from exc
            if chunk in {None, "", b""}:
                raise RuntimeError("TossInvest WebSocket closed unexpectedly; stop and reverify")
            for frame in parser.feed(chunk):
                if frame.command == "ERROR":
                    raise RuntimeError(
                        "TossInvest STOMP subscription was rejected; stop and reverify"
                    )
                if frame.command != "MESSAGE":
                    continue
                subscription = subscription_by_destination.get(
                    frame.headers.get("destination", "")
                ) or subscription_by_id.get(frame.headers.get("subscription", ""))
                if subscription is None:
                    continue
                event = normalize_message(subscription, json.loads(frame.body))
                if event is not None:
                    emit(event)
                    emitted += 1
                    if emitted >= max_events:
                        break
        return emitted
    finally:
        for subscription_id in subscribed_ids:
            try:
                socket.send(build_stomp_frame("UNSUBSCRIBE", {"id": subscription_id}))
            except Exception:
                break
        if connected:
            _disconnect_gracefully(socket, parser, websocket_module)
        try:
            socket.close()
        except Exception:
            pass


def _send_subscriptions(
    socket: Any,
    subscriptions: list[Subscription],
    subscription_ids: dict[str, str],
    subscribed_ids: list[str],
) -> None:
    for offset in range(0, len(subscriptions), SUBSCRIPTION_BATCH_SIZE):
        batch = subscriptions[offset : offset + SUBSCRIPTION_BATCH_SIZE]
        for item in batch:
            subscription_id = subscription_ids[item.destination]
            socket.send(
                build_stomp_frame(
                    "SUBSCRIBE",
                    {
                        "id": subscription_id,
                        "destination": item.destination,
                    },
                )
            )
            subscribed_ids.append(subscription_id)
        if offset + SUBSCRIPTION_BATCH_SIZE < len(subscriptions):
            time.sleep(SUBSCRIPTION_BATCH_INTERVAL_SECONDS)


def _disconnect_gracefully(socket: Any, parser: StompParser, websocket_module: Any) -> None:
    receipt_id = f"disconnect-{uuid.uuid4()}"
    try:
        socket.send(build_stomp_frame("DISCONNECT", {"receipt": receipt_id}))
    except Exception:
        return
    deadline = time.monotonic() + DISCONNECT_RECEIPT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        try:
            chunk = socket.recv()
        except websocket_module.WebSocketTimeoutException:
            continue
        except Exception:
            return
        if chunk in {None, "", b""}:
            return
        try:
            frames = parser.feed(chunk)
        except RuntimeError:
            return
        if any(
            frame.command == "RECEIPT" and frame.headers.get("receipt-id") == receipt_id
            for frame in frames
        ):
            return


def _wait_until_connected(socket: Any, parser: StompParser, websocket_module: Any) -> None:
    deadline = time.monotonic() + CONNECT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        try:
            chunk = socket.recv()
        except websocket_module.WebSocketTimeoutException:
            continue
        except getattr(websocket_module, "WebSocketConnectionClosedException", ()) as exc:
            raise RuntimeError(
                "TossInvest WebSocket closed before STOMP connected; stop and reverify"
            ) from exc
        if chunk in {None, "", b""}:
            break
        for frame in parser.feed(chunk):
            if frame.command == "CONNECTED":
                return
            if frame.command == "ERROR":
                raise RuntimeError("TossInvest STOMP connection was rejected; stop and reverify")
    raise RuntimeError("Timed out waiting for TossInvest STOMP CONNECTED")


def _load_websocket_module() -> Any:
    try:
        return importlib.import_module("websocket")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "WebSocket support is optional; install it in the project-local `.venv` "
            "as documented in references/script-cookbook.md"
        ) from exc


def _require_code(code: str, pattern: re.Pattern[str], label: str) -> None:
    if not pattern.fullmatch(code):
        raise ValueError(f"Unsupported {label} code: {code}")


def _require_public_index(code: str, allowed: frozenset[str], market: str) -> None:
    if code not in allowed:
        supported = ", ".join(sorted(allowed))
        support_note = f"public codes: {supported}" if supported else "no bounded-live public codes"
        raise ValueError(
            f"Unsupported, unconfirmed, or login-gated {market} index code: {code}; {support_note}"
        )


def _require_public_code(code: str, allowed: frozenset[str], label: str) -> None:
    if code not in allowed:
        supported = ", ".join(sorted(allowed))
        raise ValueError(f"Unsupported {label} code: {code}; public codes: {supported}")


def _unescape_header(value: str) -> str:
    replacements = {"\\": "\\", "c": ":", "n": "\n", "r": "\r"}
    return _HEADER_ESCAPE.sub(lambda match: replacements[match.group(1)], value)


def _parse_code_args(values: list[str]) -> list[str]:
    return [code.strip() for value in values for code in value.split(",") if code.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stream normalized public TossInvest trade/index/crypto updates as JSONL."
    )
    parser.add_argument("--kr-stock", action="append", default=[], help="KR product code(s)")
    parser.add_argument(
        "--us-stock",
        action="append",
        default=[],
        help="US TossInvest product/source code(s), not display tickers",
    )
    parser.add_argument(
        "--kr-index", action="append", default=[], help="Supported KR index: KGG01P or QGG01P"
    )
    parser.add_argument(
        "--us-index",
        action="append",
        default=[],
        help="Supported US index: COMP.NAI, SPX.CBI, RGI..VIX, or SOX.NAI",
    )
    parser.add_argument(
        "--crypto",
        action="append",
        default=[],
        help="Supported crypto: VWAP.KRW-BTC, VWAP.KRW-ETH, VWAP.KRW-XRP, or VWAP.KRW-SOL",
    )
    parser.add_argument("--duration", type=int, default=30, help="Run for at most 1-300 seconds")
    parser.add_argument(
        "--max-events", type=int, default=100, help="Emit at most 1-1000 normalized events"
    )
    parser.add_argument("--output", help="Write normalized JSONL to this file")
    args = parser.parse_args()

    subscriptions = build_subscriptions(
        kr_stocks=_parse_code_args(args.kr_stock),
        us_stocks=_parse_code_args(args.us_stock),
        kr_indices=_parse_code_args(args.kr_index),
        us_indices=_parse_code_args(args.us_index),
        crypto=_parse_code_args(args.crypto),
    )
    output = Path(args.output).open("w", encoding="utf-8") if args.output else sys.stdout
    emitter = JsonlEmitter(output)

    try:
        stream_prices(
            subscriptions,
            duration=args.duration,
            max_events=args.max_events,
            emit=emitter,
        )
    except KeyboardInterrupt:
        return 130
    finally:
        emitter.flush()
        if output is not sys.stdout:
            output.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
