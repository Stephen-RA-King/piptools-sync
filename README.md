# piptools-sync

---

> A pre-commit plugin to align pre-commit repository versions with those derived by pip-tools..

[![PyPI][pypi-image]][pypi-url]
[![Downloads][downloads-image]][downloads-url]
[![Status][status-image]][pypi-url]
[![Python Version][python-version-image]][pypi-url]
[![Format][format-image]][pypi-url]
[![Requirements][requirements-status-image]][requirements-status-url]
[![tests][tests-image]][tests-url]
[![Codecov][codecov-image]][codecov-url]
[![CodeFactor][codefactor-image]][codefactor-url]
[![Codeclimate][codeclimate-image]][codeclimate-url]
[![Lgtm alerts][lgtm-alerts-image]][lgtm-alerts-url]
[![Lgtm quality][lgtm-quality-image]][lgtm-quality-url]
[![CodeQl][codeql-image]][codeql-url]
[![readthedocs][readthedocs-image]][readthedocs-url]
[![pre-commit][pre-commit-image]][pre-commit-url]
[![pre-commit.ci status][pre-commit.ci-image]][pre-commit.ci-url]
[![Imports: isort][isort-image]][isort-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![security: bandit][bandit-image]][bandit-url]
[![Commitizen friendly][commitizen-image]][commitizen-url]
[![Conventional Commits][conventional-commits-image]][conventional-commits-url]
[![DeepSource][deepsource-image]][deepsource-url]
[![license][license-image]][license-url]

[**pip-tools**][pip-tools-url] and [**Pre-Commit**][pre-commit-url] are two of my favourite development tools. However, they don't always necessarily agree
on what versions of packages should be installed.
This lack of consolidation can lead to problems with pre-commit.
This pre-commit plugin syncs the pre-commit package versions with the versions generated by pip-tools' compile process.

![](assets/header.png)

## Introduction

---

### Project Rationale

A while ago I came across an issue committing files to my local git repository. The issue occured at the flake8 linting stage using pre-commit.
There was however no problem manually running flake8 from the command line. Upon investigation It was found that flake8 had an
incompatibility issue with one of its plugins.
With further investigation I noticed that pip-tools had pinned flake8 to an earlier version to what pre-commit was caching.

In short - pip-tools does a spectacularly good job pinning your dependencies and the dependencies of these dependencies. It has one job to do and it does it perfectly.
The pre-commit autoupdate command just updates the "rev" for the "repo" in the .pre-commit-config.yaml file to the latest version available and ignores the dependencies.

The following example displays the way flake8 and a few plugins are configured by the two tools :

- pip-tools (via requirements.txt)

```shell
flake8==4.0.1
    # via ...
flake8-bugbear==22.8.23
    # via ...
flake8-comprehensions==3.10.0
    # via ...
flake8-eradicate==1.3.0
    # via ...
flake8-simplify==0.19.3
    # via ...
```

- pre-commit (via .pre-commit-config.yaml)

```shell
  - repo: https://github.com/pycqa/flake8
    rev 5.0.4
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-bugbear
          - flake8-comprehensions
          - flake8-eradicate
          - flake8-simplify
        args: ["--ignore=E800,F842,F841,W503"]
```

If we force pip-tools to use a later version of flake8 (e,g 5.0.4) by manually pinning the version in the ".in" file and recompiling it is clear pip-tools is unhappy... A quick look at the dependencies shows why.

```shell
Could not find a version that matches flake8!=3.2.0,<5.0.0,<6,==5.0.4,>=3.0.0,>=3.3.0,>=3.5,>=3.7,>=3.9.1,>=4.0.1 (from -r requirements\development.in (line 12))
Tried: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.3.1, 1.4, 1.5, 1.6, 1.6.1, 1.6.2, 1.7.0, 2.0, 2.1.0, 2.2.0, 2.2.0, 2.2.1, 2.2.1, 2.2.2, 2.2.2, 2.2.3, 2.2.3, 2.2.4, 2.2.5, 2.3.0, 2.3.0, 2.4.0, 2.4.0, 2.4.1, 2.4.1, 2.5.0, 2.5.0, 2.5.1, 2.5.1, 2.5.2, 2.5.2, 2.5.3, 2.5.3, 2.5.4, 2.5.4, 2.5.5, 2.5.5, 2.6.0, 2.6.0, 2.6.1, 2.6.1, 2.6.2, 2.6.2, 3.0.0, 3.0.0, 3.0.1, 3.0.1, 3.0.2, 3.0.2, 3.0.3, 3.0.3, 3.0.4, 3.0.4, 3.1.0, 3.1.0, 3.1.1, 3.1.1, 3.2.0, 3.2.0, 3.2.1, 3.2.1, 3.3.0, 3.3.0, 3.4.0, 3.4.0, 3.4.1, 3.4.1, 3.5.0, 3.5.0, 3.6.0, 3.6.0, 3.7.0, 3.7.0, 3.7.1, 3.7.1, 3.7.2, 3.7.2, 3.7.3, 3.7.3, 3.7.4, 3.7.4, 3.7.5, 3.7.5, 3.7.6, 3.7.6, 3.7.7, 3.7.7, 3.7.8, 3.7.8, 3.7.9, 3.7.9, 3.8.0, 3.8.0, 3.8.1, 3.8.1, 3.8.2, 3.8.2, 3.8.3, 3.8.3, 3.8.4, 3.8.4, 3.9.0, 3.9.0, 3.9.1, 3.9.1, 3.9.2, 3.9.2, 4.0.0, 4.0.0, 4.0.1, 4.0.1, 5.0.0, 5.0.0, 5.0.1, 5.0.1, 5.0.2, 5.0.2, 5.0.3, 5.0.3, 5.0.4, 5.0.4
Skipped pre-versions: 3.0.0b1, 3.0.0b1, 3.0.0b2, 3.0.0b2, 3.0.2.dev0, 3.0.2.dev0, 3.0.2.dev1, 3.3.0.dev0, 3.8.0a1, 3.8.0a1, 3.8.0a2, 3.8.0a2
There are incompatible versions in the resolved dependencies:
  flake8==5.0.4 (from -r requirements\development.in (line 12))
  flake8>=3.7 (from flake8-simplify==0.19.3->-r requirements\development.in (line 20))
  flake8<5.0.0 (from flake8-bugbear==22.8.23->-r requirements\development.in (line 14))
  flake8!=3.2.0,>=3.0 (from flake8-comprehensions==3.10.0->-r requirements\development.in (line 15))
  flake8<6,>=3.5 (from flake8-eradicate==1.3.0->-r requirements\development.in (line 17))
```

The tools store packages in different areas on the file system. Pre-commit uses a cache area in the user folder, whereas pip-tools uses the usual site-packages area.

It should be noted that not all pre-commit hooks are written in Python for Python, so it makes sense that it has its own cache file system independent of pip.
Therefore, not all pre-commit repositories have an entry in PyPI. They can simply be defined by a GitHub repository URL.

Lastly, browsing the internet looking for a solution I came across the following issue raised under the pip-tools project (dated 24 Jun 2021).
The issue is still open and describes the exact same problem.

https://github.com/jazzband/pip-tools/issues/1437

## Installation

---

### 1 - Install into pre-commit

Just add to the pre-commit configuration file (.pre-commit-config.yaml).
I have configured it to run at every commit at the pre-commit stage of git.

```shell
  - repo: https://github.com/Stephen-RA-King/piptools-sync
    rev: 0.3.1
    hooks:
      - id: piptools_sync
```

### 2 - Install by pip

Installing by pip enables the package to be run from the command line at any time.

```sh
pip install piptools-sync
```

## Usage

---

### 1 - Automatic running by pre-commit

Passing example.

```shell
piptools_sync............................................................Passed
```

Failing example.

```shell
piptools_sync............................................................Failed
- hook id: piptools_sync
- exit code: 1
- files were modified by this hook

INFO:init:flake8          - piptools: 4.0.1      !=     pre-commit: 5.0.4
```

Note: In this case piptools-sync will automatically update the pre-commit config file with pip-tools version.
However, the commit with fail and will need to be re-run.

### 2 - Running from the command line

Passing example.

```shell
$ piptools_sync
Success! - pre-commit is in sync with piptools
```

Failing example.

```shell
$ piptools_sync
flake8          - piptools: 4.0.1      !=     pre-commit: 5.0.4
```

Note: In this case piptools-sync will automatically update the pre-commit config file with pip-tools version

_For more examples and usage, please refer to the [Wiki][wiki]._

## Documentation

---

### - [**Read the Docs**](https://piptools-sync.readthedocs.io/en/latest/)

### - [**Wiki**](https://github.com/Stephen-RA-King/piptools-sync/wiki)

## Future Enhancements

---

- Move some global variables into a separate settings file (toml).
- Settings configurable from the command line (and therefore configurable from the pre-commit.yaml file).
- Improve web request performance with asyncio / aiohttp libraries.

## Meta

---

[![](assets/linkedin.png)](https://linkedin.com/in/stephen-k-3a4644210)
[![](assets/github.png)](https://github.com/Stephen-RA-King)
[![](assets/pypi.png)](https://pypi.org/project/piptools-sync/)
[![](assets/www.png)](https://www.justpython.tech)
[![](assets/email.png)](mailto:stephen.ra.king@gmail.com)
[![](assets/cv.png)](https://justpython.tech/wp-content/uploads/CV.pdf)

Stephen R A King : stephen.ra.king@gmail.com

Distributed under the MIT license. See [license][license-url] for more information.

[https://github.com/Stephen-RA-King/piptools-sync](https://github.com/Stephen-RA-King/piptools-sync)

Created with Cookiecutter template: [**cc_template**][cc_template-url] version 1.2.1

<!-- Markdown link & img dfn's -->

[bandit-image]: https://img.shields.io/badge/security-bandit-yellow.svg
[bandit-url]: https://github.com/PyCQA/bandit
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black
[cc_template-url]: https://github.com/Stephen-RA-King/cc_template
[codeclimate-image]: https://api.codeclimate.com/v1/badges/9543c409696e9976a987/maintainability
[codeclimate-url]: https://codeclimate.com/github/Stephen-RA-King/piptools-sync/maintainability
[codecov-image]: https://codecov.io/gh/Stephen-RA-King/piptools-sync/branch/main/graph/badge.svg
[codecov-url]: https://app.codecov.io/gh/Stephen-RA-King/piptools-sync
[codefactor-image]: https://www.codefactor.io/repository/github/Stephen-RA-King/piptools-sync/badge
[codefactor-url]: https://www.codefactor.io/repository/github/Stephen-RA-King/piptools-sync
[codeql-image]: https://github.com/Stephen-RA-King/piptools-sync/actions/workflows/codeql-analysis.yml/badge.svg
[codeql-url]: https://github.com/Stephen-RA-King/piptools-sync/actions/workflows/codeql-analysis.yml
[commitizen-image]: https://img.shields.io/badge/commitizen-friendly-brightgreen.svg
[commitizen-url]: http://commitizen.github.io/cz-cli/
[conventional-commits-image]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square
[conventional-commits-url]: https://conventionalcommits.org
[deepsource-image]: https://static.deepsource.io/deepsource-badge-light-mini.svg
[deepsource-url]: https://deepsource.io/gh/Stephen-RA-King/piptools-sync/?ref=repository-badge
[downloads-image]: https://static.pepy.tech/personalized-badge/piptools-sync?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads
[downloads-url]: https://pepy.tech/project/piptools-sync
[format-image]: https://img.shields.io/pypi/format/piptools-sync
[isort-image]: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
[isort-url]: https://github.com/pycqa/isort/
[lgtm-alerts-image]: https://img.shields.io/lgtm/alerts/g/Stephen-RA-King/piptools-sync.svg?logo=lgtm&logoWidth=18
[lgtm-alerts-url]: https://lgtm.com/projects/g/Stephen-RA-King/piptools-sync/alerts/
[lgtm-quality-image]: https://img.shields.io/lgtm/grade/python/g/Stephen-RA-King/piptools-sync.svg?logo=lgtm&logoWidth=18
[lgtm-quality-url]: https://lgtm.com/projects/g/Stephen-RA-King/piptools-sync/context:python
[license-image]: https://img.shields.io/pypi/l/piptools-sync
[license-url]: https://github.com/Stephen-RA-King/piptools-sync/blob/main/LICENSE
[mypy-image]: http://www.mypy-lang.org/static/mypy_badge.svg
[mypy-url]: http://mypy-lang.org/
[pip-tools-url]: https://github.com/jazzband/pip-tools/
[pre-commit-image]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit-url]: https://github.com/pre-commit/pre-commit
[pre-commit.ci-image]: https://results.pre-commit.ci/badge/github/Stephen-RA-King/piptools-sync/main.svg
[pre-commit.ci-url]: https://results.pre-commit.ci/latest/github/Stephen-RA-King/piptools-sync/main
[pypi-url]: https://pypi.org/project/piptools-sync/
[pypi-image]: https://img.shields.io/pypi/v/piptools-sync.svg
[python-version-image]: https://img.shields.io/pypi/pyversions/piptools-sync
[readthedocs-image]: https://readthedocs.org/projects/piptools-sync/badge/?version=latest
[readthedocs-url]: https://piptools-sync.readthedocs.io/en/latest/?badge=latest
[requirements-status-image]: https://requires.io/github/Stephen-RA-King/piptools-sync/requirements.svg?branch=main
[requirements-status-url]: https://requires.io/github/Stephen-RA-King/piptools-sync/requirements/?branch=main
[status-image]: https://img.shields.io/pypi/status/piptools-sync.svg
[tests-image]: https://github.com/Stephen-RA-King/piptools-sync/actions/workflows/tests.yml/badge.svg
[tests-url]: https://github.com/Stephen-RA-King/piptools-sync/actions/workflows/tests.yml
[wiki]: https://github.com/Stephen-RA-King/piptools-sync/wiki
