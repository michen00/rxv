#!/usr/bin/env python
"""Archive URLs to the configured archive services.

Example usage:
    $ rxv https://example.com
    $ rxv http://example1.com http://example2.org
    $ rxv https://example.com --all
    $ rxv https://example.com --archivetoday --internetarchive
    $ echo https://example.com | rxv
"""

__all__ = []

import logging
from datetime import UTC, datetime
from itertools import product
from random import shuffle
from sys import stdin
from typing import Annotated, Optional
from urllib.parse import urlparse

import structlog
import typer
from pydantic import AnyHttpUrl, ValidationError
from rxv.config import EXCLUDED_DOMAINS
from rxv.core import SupportedServices, archive_with
from tqdm.auto import tqdm
from typer import Argument, Option

logging.basicConfig(
    filename=f"{datetime.now(tz=UTC).date().isoformat()}.log",
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()


def main(
    urls: Annotated[
        Optional[list[str]],  # noqa: UP007
        Argument(help="URLs to archive. If empty, reads from stdin."),
    ] = None,
    *,
    archivetoday: Annotated[
        bool,
        Option(
            f"--{SupportedServices.ARCHIVETODAY}",
            "--at",
            help="enable archive.today",
        ),
    ] = False,
    internetarchive: Annotated[
        bool,
        Option(
            f"--{SupportedServices.INTERNETARCHIVE}",
            "--ia",
            help="enable Internet Archive Wayback Machine",
        ),
    ] = False,
    all_services: Annotated[
        bool,
        Option("--all", "-a", help="enable all archival services"),
    ] = False,
    verbose: Annotated[
        bool,
        Option("--verbose", "-v", help="enable verbose logging"),
    ] = True,
) -> None:
    """Provide the entry point for the CLI."""
    if not urls:
        urls = {_url for url in stdin.readlines() if (_url := url.strip())}
    if not urls:
        msg = "No URLs provided."
        logger.error(msg)
        typer.echo(msg)
        raise typer.Exit(1)

    _urls = set()
    include_url = _urls.add
    for url in urls:
        if urlparse(url).netloc in EXCLUDED_DOMAINS:
            logger.warning("Excluded URL by domain", url=url)
            continue
        try:
            AnyHttpUrl(url)
        except ValidationError as e:
            logger.warning("Invalid URL", url=url, exc_info=e)
            continue
        include_url(url)
    urls = _urls

    if not urls:
        logger.info("No valid URLs to archive")
        raise typer.Exit(0)

    services = []
    if all_services:
        services = [*SupportedServices]
    else:
        if archivetoday:
            services.append(SupportedServices.ARCHIVETODAY)
        if internetarchive:
            services.append(SupportedServices.INTERNETARCHIVE)
        if not services:
            services = [*SupportedServices]

    failure, success = "Failed to archive URL", "Archived URL"
    urls_x_services: list[tuple] = [*product(urls, services)]
    shuffle(urls_x_services)
    if verbose:
        for url, service in tqdm(urls_x_services, desc="Archiving URLs..."):
            typer.echo(f"Archiving {url} with {service}")
            response: tuple | None = archive_with(service, url)
            timestamp: str = datetime.now(tz=UTC).isoformat()
            if failed := (response is None):
                logger.error(
                    failure,
                    url=url,
                    service=service,
                    timestamp=timestamp,
                )
            else:
                logger.info(
                    success,
                    url=url,
                    service=service,
                    archive_url=response.archive_url,
                    response=response.response,
                    timestamp=timestamp,
                )
            print(  # noqa: T201
                f"{failure if failed else success} ({service.name}): {url}"
                f'{f" -> {response.archive_url}" if response else ""}',
            )
    else:  # this should be roughly equivalent to the verbose block
        log_error, log_info = logger.error, logger.info
        for url, service in urls_x_services:
            log_error(
                failure,
                url=url,
                service=service,
                timestamp=timestamp,
            ) if (response := archive_with(service, url)) is None else log_info(
                success,
                url=url,
                service=service,
                archive_url=response.archive_url,
                timestamp=timestamp,
            )


def rxv() -> None:
    """Provide the entry point for the CLI."""
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
