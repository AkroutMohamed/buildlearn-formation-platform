"""Endpoint-only transport and snapshot lifecycle; validated algorithms unchanged."""
from threading import RLock
from urllib.parse import urlsplit
import ipaddress
import socket

from app.ai.retrieval.retrieval_v2 import RetrievalV2


def local_transport_url(url):
    """Avoid IPv6 connection fallback for the local HTTP services.

    HTTPS, remote hosts, credentials, ports, paths and query strings are preserved.
    Application configuration remains unchanged; only the local client address differs.
    """
    parsed = urlsplit(url)
    if parsed.scheme == 'http' and parsed.hostname == 'localhost' and parsed.username is None:
        try:
            addresses = {entry[4][0] for entry in socket.getaddrinfo('localhost', parsed.port or 80,
                                                                  type=socket.SOCK_STREAM)}
        except OSError:
            return url
        if '127.0.0.1' in addresses and all(ipaddress.ip_address(a).is_loopback for a in addresses):
            return parsed._replace(netloc='127.0.0.1' + (':' + str(parsed.port) if parsed.port else '')).geturl()
    return url


class RuntimeRetrievalV2(RetrievalV2):
    """Single initialization with concurrent warm retrieval and no result cache.

    An explicit refresh replaces the snapshot atomically. A changed client identity
    discards it. The existing dense/payload consistency guard still fails closed;
    on that failure the stale snapshot is evicted, never silently retried.
    Parent verification continues on every request without caching evidence.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lifecycle_lock = RLock()
        self._snapshot_client = self.client

    def refresh(self):
        with self._lifecycle_lock:
            # A failed refresh must not leave a previously valid snapshot usable.
            self._index = None
            self._v1._client = self.client
            digest = super().refresh()
            self._snapshot_client = self.client
            return digest

    def retrieve(self, query, *, top_k=None, mode='v2'):
        if not isinstance(query, str) or not query.strip():
            raise ValueError('Query must be nonempty')
        k = self.config.top_k if top_k is None else top_k
        if type(k) is not int or k < 1:
            raise ValueError('top_k must be a positive integer')
        if mode not in ('v2', 'lexical', 'identifier_lexical'):
            raise ValueError('Unsupported retrieval mode')
        with self._lifecycle_lock:
            if self.client is not self._snapshot_client:
                self._index = None
                self._v1._client = self.client
                self._snapshot_client = self.client
            if self._index is None:
                self.refresh()
            # Existing lazy provider probes dimension once; protect its initialization.
            if mode == 'v2' and self._v1._embeddings is None:
                self._v1._embedding_service()
            snapshot = self._index
        try:
            return super().retrieve(query, top_k=top_k, mode=mode)
        except ValueError as exc:
            if str(exc) == 'Dense payload differs from lexical snapshot; refresh required':
                with self._lifecycle_lock:
                    if self._index is snapshot:
                        self._index = None
            raise
