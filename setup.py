#!/usr/bin/env python3

import sys

from setuptools import setup

assert sys.version_info >= (3, 7), "olx-crawler requires Python 3.7+"  # nosec
from pathlib import Path  # noqa E402

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta


def get_long_description() -> str:
    return (CURRENT_DIR / "README.md").read_text(encoding="utf8")


if __name__ == "__main__":
    setup(
        version="1.0.0",
        name="olx-crawler",
        description=(
            "An easy-to-use, powerful crawler for OLX, that allows collecting "
            "various non-sensitivity data about ads on the site."
        ),
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        author="Eduard Malokhvii",
        author_email="malokhvii.ee@gmail.com",
        url="https://github.com/malokhvii-eduard/olx-crawler",
        license="MIT",
        py_modules=["olx"],
        python_requires=">= 3.7",
        install_requires=[
            "ahocorapy>=1.6.1",
            "click>=8.0.3",
            "inject>=4.3.1",
            "selenium>=4.1.0",
            "tqdm>=4.62.3",
            "validators>=0.18.2",
            "webdriver-manager>=3.5.2",
        ],
        entry_points={
            "console_scripts": [
                "olx=olx:cli",
            ]
        },
    )
