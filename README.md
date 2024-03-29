<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD041 -->

<div align="center">
  <h2 align="center">🤖 OLX Crawler</h2>
  <p align="center">
    An easy-to-use, powerful crawler for
    <a href="https://olx.ua" aria-label="OLX">OLX</a>, that allows collecting
    various non-sensitive data about ads on the site.
  </p>

  <p id="shields" align="center" markdown="1">

[![License](https://img.shields.io/badge/license-MIT-3178C6?style=flat)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][github-pre-commit]
[![pre-commit.ci](https://results.pre-commit.ci/badge/github/malokhvii-eduard/olx-crawler/master.svg)][pre-commit.ci]
[![Style Guide](https://img.shields.io/badge/code%20style-black-000?style=flat)][github-black]
[![markdownlint](https://img.shields.io/badge/linter-markdownlint-000?style=flat)][github-markdownlint]
[![commitlint](https://img.shields.io/badge/linter-commitlint-F7B93E?style=flat)][github-commitlint]
[![flake8](https://img.shields.io/badge/linter-flake8-3776AB?style=flat)][github-flake8]
[![bandit](https://img.shields.io/badge/linter-bandit-FFC107?style=flat)][github-bandit]

  </p>
</div>

## 🎉 Features

- 🦾 Enough performance
- 🎭 Anonymous, especially via [Tor][tor]
- ⚖️ Non-sensitive data
- 🔍 Filtering by keywords
- ⛓️ Commands chaining

## 🌻 Motivation

Demonstration of experience with [Selenium][github-selenium] for Web Scraping
💪. Analyzing non-sensitive data about ads on the site 🧐. No ready solutions
for collecting data from the site 😢.

## ✨ Getting Started

### 📚 Prerequisites

You will need to install only [Google Chrome][google-chrome], thats all. No
need manual installation of WebDriver binary.
[@SergeyPirogov](https://github.com/SergeyPirogov) thank you for
[WebDriver Manager][github-webdriver-manager].

### 📦 Installation

1. Clone the *Repository*
2. Install this *Package* (`./setup.py install`) or install dependencies from
[Pipfile](Pipfile) (`pipenv install`)

### 👀 Usage

<!-- markdownlint-disable MD013 -->
```bash
olx ads --help # Show help for ads command and exit
olx ads "https://www.olx.ua/uk/zhivotnye/koshki/" # Collect all ads with cats
olx ads --no-free ... # Only paid ads
olx ads --no-paid ... # Only free ads
olx ads --kind --title --price --location ... # Collect extra fields

olx ad --help # Show help for ad command and exit
olx ad "https://www.olx.ua/d/uk/obyavlenie/laskovye-shotlandskie-malyshi-IDNyrf4.html" # Collect ad details
olx ad --keywords keywords.txt ... # Filter by keywords
olx ad --title --description --author --profile --price --location ... # Collect extra fields

olx ads --progress ... # Show progress
olx ads --no-headless ... # Disabled headless mode
olx ads --proxy "socks5://..." # Use proxy server
olx ads --all ... # Collect all fields
olx ads --no-link ... # Skip link field
olx ads "https://www.olx.ua/uk/zhivotnye/koshki/" | olx ad --all --progress > ads.csv # Commands chaining
```
<!-- markdownlint-enable MD013 -->

## 🛠️ Tech Stack

<!-- markdownlint-disable MD013 -->
[![EditorConfig](https://img.shields.io/badge/EditorConfig-FEFEFE?logo=editorconfig&logoColor=000&style=flat)][editorconfig]
![Markdown](https://img.shields.io/badge/Markdown-000?logo=markdown&logoColor=fff&style=flat)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=flat)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=fff&style=flat)][github-selenium]
[![click](https://img.shields.io/badge/click-4EAA25?logo=gnubash&logoColor=fff&style=flat)][github-click]
[![tqdm](https://img.shields.io/badge/tqdm-FFC107?logo=tqdm&logoColor=000&style=flat)][github-tqdm]
[![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?logo=precommit&logoColor=fff&style=flat)][github-pre-commit]
[![markdownlint](https://img.shields.io/badge/markdownlint-000?logo=markdown&logoColor=fff&style=flat)][github-markdownlint]
[![commitlint](https://img.shields.io/badge/commitlint-F7B93E?logo=c&logoColor=000&style=flat)][github-commitlint]
[![Shields.io](https://img.shields.io/badge/Shields.io-000?logo=shieldsdotio&logoColor=fff&style=flat)][shields]
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=fff&style=flat)][git-scm]
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=fff&style=flat)][github]
<!-- markdownlint-enable MD013 -->

## ✍️ Contributing

👍🎉 *First off, thanks for taking the time to contribute!* 🎉👍

Contributions are what make the open source community such an amazing place to
be learn, inspire, and create. Any contributions you make are **greatly
appreciated**.

1. Fork the *Project*
2. Create your *Feature Branch* (`git checkout -b feature/awesome-feature`)
3. Commit your *Changes* (`git commit -m 'Add awesome feature'`)
4. Push to the *Branch* (`git push origin feature/awesome-feature`)
5. Open a *Pull Request*

## 💖 Like this project?

Leave a ⭐ if you think this project is cool or useful for you.

## ⚠️ License

`olx-crawler` is licenced under the MIT License. See the [LICENSE](LICENSE)
for more information.

<!-- markdownlint-disable MD013 -->
<!-- Github links -->
[github-bandit]: https://github.com/PyCQA/bandit
[github-black]: https://github.com/psf/black
[github-click]: https://github.com/pallets/click
[github-commitlint]: https://github.com/conventional-changelog/
[github-flake8]: https://github.com/PyCQA/flake8
[github-markdownlint]: https://github.com/DavidAnson/markdownlint
[github-pre-commit]: https://github.com/pre-commit/pre-commit
[github-selenium]: https://github.com/SeleniumHQ/selenium
[github-tqdm]: https://github.com/tqdm/tqdm
[github-webdriver-manager]: https://github.com/SergeyPirogov/webdriver_manager
[github]: https://github.com

<!-- Other links -->
[editorconfig]: https://editorconfig.org
[git-scm]: https://git-scm.com
[google-chrome]: https://www.google.com/intl/en/chrome/
[pre-commit.ci]: https://results.pre-commit.ci/run/github/445843501/1679335481.yUkXnHaaRvqilq37bpU95w
[shields]: https://shields.io
[tor]: https://www.torproject.org/
