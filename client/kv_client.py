import time
import random
import requests
from typing import Optional


class KVClientError(Exception):
    pass


class RateLimitError(KVClientError):
    pass


class KVClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 5,
        backoff_base: float = 0.5,
        jitter: float = 0.3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.jitter = jitter

    # --------------------------------------------------
    # Internal request handler with retries
    # --------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ):
        url = f"{self.base_url}{path}"

        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                )

                # Rate limit handling
                if response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")

                # Success
                if response.status_code < 400:
                    return response.json()

                # Client errors (do not retry)
                if 400 <= response.status_code < 500:
                    raise KVClientError(
                        f"{response.status_code}: {response.text}"
                    )

                # Server errors → retry
                raise KVClientError(
                    f"Server error {response.status_code}"
                )

            except RateLimitError:
                # Always retry rate limits
                delay = self._backoff_delay(attempt)
                time.sleep(delay)

            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    KVClientError) as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self._backoff_delay(attempt)
                time.sleep(delay)

        raise KVClientError("Max retries exceeded")

    def _backoff_delay(self, attempt: int) -> float:
        exponential = self.backoff_base * (2 ** attempt)
        jitter = random.uniform(0, self.jitter)
        return exponential + jitter

    # --------------------------------------------------
    # Public API methods
    # --------------------------------------------------

    def create(self, key: str, value: str):
        """
        POST /items/
        """
        return self._request(
            "POST",
            "/items/",
            json={"key": key, "value": value},
        )

    def get(self, key: str):
        """
        GET /items/{key}
        """
        return self._request(
            "GET",
            f"/items/{key}",
        )

    def update(self, key: str, value: str):
        """
        PUT /items/{key}
        """
        return self._request(
            "PUT",
            f"/items/{key}",
            params={"value": value},
        )

    def delete(self, key: str):
        """
        DELETE /items/{key}
        """
        return self._request(
            "DELETE",
            f"/items/{key}",
        )

    def list(self, page: int = 1, page_size: int = 10):
        """
        GET /items/?page=&page_size=
        """
        return self._request(
            "GET",
            "/items/",
            params={"page": page, "page_size": page_size},
        )
