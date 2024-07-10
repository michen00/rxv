# rxv

wip

A tool for sending URLs to online archives

## Currently supported

| service                                 | parameter           |
| :-------------------------------------- | :------------------ |
| [archive.today](https://archive.today)  | `"archivetoday"`    |
| [Internet Archive](https://archive.org) | `"internetarchive"` |

## Installation

```terminal
python -m pip install rxv
```

## Usage

```terminal
rxv https://example.com --archivetoday --internetarchive
rxv https://example.com --at --it
rxv http://example1.com http://example2.com
echo https://example.com | rxv
```

```python
import rxv

url = "https://example.com"
rxv.archive_with_internetarchive(url)
rxv.archive_with_archivedottoday(url)
result = rxv.archive_with("internetarchive", url)
print(result.response, result.archive_url)
```

## Setup

- `make install`: install the package.
- `make develop`: install in editable mode.
- `make check`: run the test suite (requires installation with `make develop` rather than `make install`).
- `make uninstall`: uninstall the package.
- `make clean`: clean the build files.

## TODO

- idempotency
- concurrency
- improve implementations (e2a for internetarchive?)
- add tests
- add more archival services
