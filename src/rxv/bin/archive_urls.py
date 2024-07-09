#!/usr/bin/env python
"""Archive URLs to the configured archive services."""

__all__ = []

import asyncio
from collections.abc import Iterable
from urllib.parse import urlparse

import structlog
import typer
from rxv.config import EXCLUDED_DOMAINS
from rxv.core import archive_urls

app = typer.Typer()

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


@app.command()
def command(urls: list[str], batch_size: int = 5) -> None:
    """Archive URLs to the Internet Archive and archive.today.

    Args:
        urls: List of URLs to archive.
        batch_size: Number of URLs to process in each batch.
    """
    filtered_urls = filter_urls(urls)
    if not filtered_urls:
        logger.warning("No valid URLs to archive")
        raise typer.Exit(code=1)
    logger.info("Archiving URLs", batch_size=batch_size, urls=filtered_urls)
    asyncio.run(archive_urls(filtered_urls, batch_size))


def main() -> None:
    """Provide the entry point for the CLI."""
    app()


if __name__ == "__main__":
    app()
