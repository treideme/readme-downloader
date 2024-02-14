# Readme.io Docs Downloader

[![Continous Integration](https://github.com/treideme/readme-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/treideme/readme-downloader/actions/workflows/ci.yml)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![GitHub](https://img.shields.io/github/license/treideme/readme-downloader)](LICENSE.md)
[![GitHub issues](https://img.shields.io/github/issues/treideme/readme-downloader)](

This script will download all the documentation / guides and readme-stored images to
a directory of your choice.

Usage
```bash
python3 readme_downloader.py --token <your token> --dir <output directory>
```

You can also use this script as GitHub action. Just add the following to your workflow file:
```yaml
name: My Workflow
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run The Docs Downloader
      uses: treideme/readme-downloader@master
      with:
        path: 'docs'
        token: ${{ secrets.README_TOKEN }}
```

Note this script is in its early stages and may not work for all cases. If you find a bug or desire a feature, 
please open an issue.


