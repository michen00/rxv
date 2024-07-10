"""functions for archiving URLs with various services."""

__all__ = "archive_with", "archive_with_archivetoday", "archive_with_internetarchive"

from secrets import token_hex
from typing import Any, Literal, NamedTuple

import requests
import structlog
from eprints2archives.services import archivetoday as e2a
from pydantic import AnyHttpUrl, validate_call
from waybackpy import WaybackMachineSaveAPI


class ArchiveToday(e2a.ArchiveToday):
    """Archive.today API client.

    Adapted from https://github.com/caltechlibrary/eprints2archives/
        blob/main/eprints2archives/services/archivetoday.py (20240709 38437d3)

    Modifies the save method to save the response and return the archival URL.
    """

    __slots__ = ("response",)

    def __init__(self) -> None:
        self.response: requests.Response | None = None
        super().__init__()

    def save(self, url: AnyHttpUrl, retry: int = 0) -> AnyHttpUrl | None:
        if self._available and self._host is None:
            self._host = self._archive_host()
            self._available = self._host is not None
        response, error = e2a.net(
            "post",
            f"https://{self._host}/submit/",
            handle_rate=False,
            headers={"User-Agent": token_hex(6)},
            data={
                "anyway": 1,
                "submitid": self._sid,
                "url": url,
            },  # do not change the key order
        )
        self.response = response

        if error:
            # Archive.today doesn't return code 429 when you hit the rate limit
            # and instead throws code 503. See author's posting of 2020-08-04:
            # https://blog.archive.today/post/625519838592417792
            if isinstance(error, e2a.ServiceFailure):
                e2a.wait(e2a._RATE_LIMIT_SLEEP)
                return self.save(url, retry)

            # Our underlying net(...) function will retry automatically for
            # some recognizable temporary problems. Others, we handle here.
            retry += 1
            if e2a._MAX_RETRIES - retry > 0:
                e2a.wait(e2a._RETRY_SLEEP * pow(retry, 2))
                return self.save(url, retry)
            raise error

        if "Refresh" in response.headers:
            return str(response.headers["Refresh"]).split(";url=")[1]
        if "Location" in response.headers:
            return str(response.headers["Location"])

        for h in response.history:
            if "Location" in h.headers:
                return str(h.headers["Location"])

        return None


logger = structlog.get_logger()


class ArchiveResponse(NamedTuple):
    """Response from an archive request."""

    response: requests.Response | None = None
    archive_url: AnyHttpUrl | None = None


def archive_with(
    service: Literal["archive_dot_today", "internetarchive"],
    url: AnyHttpUrl,
    *args: tuple[Any, ...],
    **kwargs: dict[str, Any],
) -> ArchiveResponse | None:
    """Archive a URL with a specified service.

    Args:
        service: Archive service to use.
        client: HTTP client to use for sending requests.
        url: URL to archive.
        *args: Additional arguments to pass to the archive function.
        **kwargs: Additional keyword arguments to pass to the archive function.

    Returns:
        ArchiveResponse: A tuple of the response and the archival URL. If the
            archival request fails, None is returned.
    """
    try:
        match service:
            case "archive_dot_today":
                return archive_with_archivetoday(url)
            case "internetarchive":
                return archive_with_internetarchive(url)
    except Exception as e:
        logger.exception(
            "Failed to obtain a response",
            url=url,
            service=service,
            exc_info=e,
            args=args,
            kwargs=kwargs,
        )
    return None


@validate_call
def archive_with_archivetoday(url: AnyHttpUrl, /) -> ArchiveResponse:
    """Archive a URL with archive.today.

    Args:
        url: URL to archive.

    Returns:
        ArchiveResponse: A tuple of the response and the archival URL.
    """
    client = ArchiveToday()
    archive_url = client.save(url)
    return ArchiveResponse(client.response, archive_url)


@validate_call
def archive_with_internetarchive(url: AnyHttpUrl, /) -> ArchiveResponse:
    """Archive a URL with the Internet Archive's Wayback Machine.

    Args:
        url: URL to archive.

    Returns:
        ArchiveResponse: A tuple of the response and the archival URL.
    """
    client = WaybackMachineSaveAPI(url, token_hex(6))
    archive_url = client.save()
    return ArchiveResponse(client.response, archive_url)
