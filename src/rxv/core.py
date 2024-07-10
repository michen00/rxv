"""functions for archiving URLs with various services."""

__all__ = "archive_with", "archive_with_archivetoday", "archive_with_internetarchive"

from secrets import token_hex
from typing import Any, Literal, NamedTuple

import requests
import structlog
from pydantic import AnyHttpUrl, validate_call
from waybackpy import WaybackMachineSaveAPI

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
                archive_response = archive_with_archivetoday(url)
            case "internetarchive":
                archive_response = archive_with_internetarchive(url)
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
    return archive_response


@validate_call
def archive_with_archivetoday(url: AnyHttpUrl) -> requests.Response:
    """Archive a URL with archive.today.

    Args:
        client: HTTP client to use for sending requests.
        url: URL to archive.
    """
    # TODO: implement


@validate_call(validate_return=True)
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
