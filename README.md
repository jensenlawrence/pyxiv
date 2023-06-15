# pyxiv

## Description
`pyxiv` is a Python library that interfaces with the [arXiv API](https://info.arxiv.org/help/api/user-manual.html), allowing for papers to be searched for and downloaded using Python scripts. The library is lightweight and geared towards simple use cases (e.g. automating a weekly download of all the papers about your favourite topic that have been submitted in the past week).

## Installation
This library is currently not on PyPI, but can be cloned directly from GitHub. This library has two external dependencies: [requests](https://requests.readthedocs.io/en/latest/) and [feedparser](https://feedparser.readthedocs.io/en/latest/); all other dependencies are part of the Python Standard Library.

## Usage
Tutorials on how to use `pyxiv` can be found in [examples](https://github.com/jensen-lawrence/pyxiv/tree/main/examples). A basic example, though, is the following:
```python
from pyxiv import Search

search = Search(
  query      = "all:protoplanetary disks",
  start_date = "2023-01-01"
)

search.download_results("./papers")
```
This code identifies all papers submitted to [arxiv.org](https://arxiv.org) since January 1, 2023 that contain the phrase 'protoplanetary disks' in any of their fields, and downloads .pdf files of these papers to the directory `./papers`.
