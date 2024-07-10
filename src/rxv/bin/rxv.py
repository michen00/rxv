#!/usr/bin/env python
"""Archive URLs to the configured archive services.

Example usage:
    $ rxv https://example.com
    $ rxv http://example1.com http://example2.org
    $ rxv https://example.com --all
    $ rxv https://example.com --internetarchive --archivetoday
"""

__all__ = []

import asyncio
from collections.abc import Iterable
from itertools import product
from typing import Annotated
from urllib.parse import urlparse

import structlog
import typer
from rxv.config import EXCLUDED_DOMAINS
from rxv.core import SupportedServices, archive_with
from tqdm.auto import tqdm
from typer import Argument, Option

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


def filter_urls(urls: Iterable[str]) -> list[str]:
    """Filter out URLs from the excluded domains.

    Args:
        urls: List of URLs to filter.

    Returns:
        Deduplicated URLs that are not in the excluded domains.
    """
    return [*{url for url in urls if urlparse(url).netloc not in EXCLUDED_DOMAINS}]


def main(
    urls: Annotated[list[str], Argument(help="URLs to archive")],
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
        Option("--verbose", "-v", help="enable printing status messages to stdout"),
    ] = True,
) -> None:
    """Provide the entry point for the CLI."""
    urls = filter_urls(urls)
    if not urls:
        logger.error("No valid URLs to archive")
        raise typer.Exit(code=1)

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
    if verbose:
        for url, service in tqdm(product(urls, services), desc="Archiving URLs..."):
            response = archive_with(service, url)
            if failed := response is None:
                logger.error(failure, url=url, service=service)
            else:
                logger.info(
                    success,
                    url=url,
                    service=service,
                    archive_url=response.archive_url,
                )
            print(
                f"{failure if failed else success} ({service.name}): {url}"
                f'{f" -> {response.archive_url}" if response else ""}',
            )
    else:
        for url, service in product(urls, services):
            response = archive_with(service, url)
            if response is None:
                logger.error(failure, url=url, service=service)
            else:
                logger.info(
                    success,
                    url=url,
                    service=service,
                    archive_url=response.archive_url,
                )


def rxv() -> None:
    """Provide the entry point for the CLI."""
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
