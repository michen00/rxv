"""Provide configuration for the rxv package."""

__all__ = ["EXCLUDED_DOMAINS"]

from typing import Final

_ARCHIVE_TODAY: Final = {"archive.is", "archive.org", "archive.ph", "archive.today"}
_INTERNET_ARCHIVE: Final = {"web.archive.org"}

EXCLUDED_DOMAINS: Final = {*_ARCHIVE_TODAY, *_INTERNET_ARCHIVE}
