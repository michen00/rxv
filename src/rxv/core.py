"""core functions"""

# __all__: list = []

from enum import IntEnum, auto

import structlog

logger = structlog.get_logger()


class _Status(IntEnum):
    """Status codes for the result of an archive request."""

    SUCCESS = auto()
    FAILURE = auto()


class _InvalidServiceError(ValueError):
    """Exception raised when an unknown service is provided."""

    def __init__(self, service: str) -> None:
        """Initialize the exception.

        Args:
            service: Service that was provided.
        """
        super().__init__(f"Unknown service: {service}")


def archive_with(service, client, url) -> _Status:
    """Archive a URL with a specified service.

    Args:
        service: Archive service to use.
        client: HTTP client to use for sending requests.
        url: URL to archive.
    """
    status = _Status.FAILURE
    try:
        match service:
            case "internetarchive":
                archive_with_internetarchive(client, url)
            case "archivetoday":
                archive_with_archivetoday(client, url)
            case __:
                raise _InvalidServiceError(service)
        status = _Status.SUCCESS  # TODO: depend on response
    except Exception as e:
        logger.exception(
            "Failed to archive URL",
            url=url,
            exc_info=e,
        )
    # if reponse is good:
    #     status = _Status.SUCCESS
    return status


def archive_with_internetarchive(client, url):
    """Archive a URL with the Internet Archive.

    Args:
        client: HTTP client to use for sending requests.
        url: URL to archive.
    """
    # TODO: implement


def archive_with_archivetoday(client, url):
    """Archive a URL with archive.today.

    Args:
        client: HTTP client to use for sending requests.
        url: URL to archive.
    """
    # TODO: implement
