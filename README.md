# rxv

wip

A tool for sending URLs to online archives

## Currently supported (wip)

| service                                 | parameter             |
| :-------------------------------------- | :-------------------- |
| [archive.today](https://archive.today)  | `"archive_dot_today"` |
| [Internet Archive](https://archive.org) | `"internetarchive"`   |

## Installation (not ready yet)

```terminal
python -m pip install rxv
```

## Usage

`rxv [options] <url>`

```terminal
rxv https://example.com
rxv http://example1.com http://example2.com
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

- finish implementations
- improve options for toggling archival services
- add tests
- add more archival services
