#!/usr/bin/env python3

import csv
import logging
import sys
from contextlib import contextmanager
from functools import wraps
from itertools import chain
from typing import TextIO, Generator, Optional, Tuple, List, Set, Dict, Any

import click
import inject
from ahocorapy.keywordtree import KeywordTree
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    presence_of_all_elements_located,
)
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from validators.url import url
from webdriver_manager.chrome import ChromeDriverManager


# ------------------------------------------------------------------------------------ #


def get_links(
    links: Tuple[str, ...], progress: bool = False, stdin: TextIO = sys.stdin
) -> Generator[str, None, None]:
    if not links and stdin.isatty():
        sys.exit(1)

    links = links if links else stdin
    links = filter(lambda l: url(l), map(lambda l: l.strip(), links))
    links = tqdm(links) if progress else links

    for link in links:
        yield link


def create_fieldnames(fields: Dict[str, bool], all: bool = False) -> Set[str]:
    fields = dict(map(lambda f: (f, True), fields.keys())) if all else fields
    return set(map(lambda f: f[0], filter(lambda f: f[1], fields.items())))


@inject.autoparams("fieldnames")
def add_field(
    item: Dict[str, Any], fieldname: str, getter: Any, fieldnames: Set[str]
) -> Dict[str, Any]:
    item[fieldname] = getter() if fieldname in fieldnames else None
    return item


def filter_fields(item: Dict[str, any], fieldnames: Set[str]) -> Dict[str, Any]:
    filtered = set(item.keys()).intersection(fieldnames)
    return dict(map(lambda f: (f, item[f]), filtered))


@inject.autoparams("fieldnames")
def csv_writer(
    fieldnames: Set[str], stdout: TextIO = sys.stdout
) -> Generator[None, Optional[Dict[str, Any]], None]:
    writer = csv.DictWriter(stdout, list(sorted(fieldnames)))
    writer.writeheader()

    while True:
        item: Optional[Dict[str, Any]] = yield
        if item:
            writer.writerow(filter_fields(item, fieldnames))
            stdout.flush()


def create_keywords_tree(keywords: TextIO) -> KeywordTree:
    keywords_tree = KeywordTree(case_insensitive=True)
    for keyword in keywords:
        keywords_tree.add(keyword.strip())

    keywords_tree.finalize()
    return keywords_tree


def has_keywords(item: Optional[Dict[str, Any]], keywords_tree: KeywordTree) -> bool:
    if item is None:
        return False

    title, description = item["title"], item["description"]
    title = "" if title is None else title
    description = "" if description is None else description
    return keywords_tree.search_one(" ".join([title, description]))


def return_on_failure(*exceptions, return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions:
                return return_value

        return wrapper

    return decorator


# ------------------------------------------------------------------------------------ #
# Locators
# ------------------------------------------------------------------------------------ #

FREE_ADS = (By.CSS_SELECTOR, ".offer:not(.promoted)")
PAID_ADS = (By.CSS_SELECTOR, ".offer.promoted")
NEXT_ADS_PAGE = (
    By.XPATH,
    "//span[@data-cy='page-link-current']/../following-sibling::span[1]/a",
)

AD_LINK = (By.TAG_NAME, "a")
AD_TITLE = (By.CSS_SELECTOR, ".title-cell strong")
AD_PRICE = (By.CSS_SELECTOR, ".price strong")
AD_LOCATION = (By.XPATH, "//i[@data-icon='location-filled']/..")

AD_DETAILS_CONTENT = (By.CSS_SELECTOR, "header ~ div:first-of-type")
AD_DETAILS_TITLE = (By.XPATH, "//h1[@data-cy='ad_title']")
AD_DETAILS_DESCRIPTION = (By.XPATH, "//div[@data-cy='ad_description']/div")
AD_DETAILS_PRICE = (By.XPATH, "//div[@data-testid='ad-price-container']/h3")
AD_DETAILS_AUTHOR = (By.XPATH, "//a[@name='user_ads']/div/div/h2")
AD_DETAILS_PROFILE = (By.XPATH, "//a[@name='user_ads']")
AD_DETAILS_LOCATION = (By.CSS_SELECTOR, ".qa-static-ad-map-container > img")
AD_DETAILS_OPEN_LOGIN = (By.XPATH, "//button[@data-testid='login-button']")

# ------------------------------------------------------------------------------------ #


@contextmanager
def chrome(headless: bool = False, proxy: Optional[str] = None) -> Chrome:
    executable = ChromeDriverManager(log_level=logging.CRITICAL).install()
    service = Service(executable)

    options = ChromeOptions()
    options.add_argument("--silent")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-certificate-errors-spki-list")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--window-size=1366,768")
    options.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"]
    )
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option(
        "prefs",
        {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.cookies": 1,
            "profile.managed_default_content_settings.stylesheets": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
        },
    )

    if headless:
        options.add_argument("--headless")

        if sys.platform == "win32":
            options.add_argument("--disable-gpu")

    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    if sys.platform.startswith("linux"):
        options.add_argument("--disable-dev-shm-usage")

    driver = Chrome(service=service, options=options)

    try:
        yield driver
    finally:
        driver.quit()


@inject.autoparams("driver")
@return_on_failure(TimeoutException, return_value=[])
def find_ads(
    locator: Tuple[str, str], driver: WebDriver, timeout: int = 30
) -> List[WebElement]:
    return WebDriverWait(driver, timeout).until(
        presence_of_all_elements_located(locator)
    )


def find_free_ads(skip: bool = False) -> List[WebElement]:
    return find_ads(FREE_ADS) if not skip else []


def find_paid_ads(skip: bool = False) -> List[WebElement]:
    return find_ads(PAID_ADS) if not skip else []


@inject.autoparams("driver")
@return_on_failure(TimeoutException)
def find_next_ads_page(driver: WebDriver, timeout: int = 5) -> Optional[str]:
    next_page: WebElement = WebDriverWait(driver, timeout).until(
        presence_of_element_located(NEXT_ADS_PAGE)
    )
    return next_page.get_attribute("href")


@inject.autoparams("driver")
@return_on_failure(TimeoutException)
def find_ad_details_content(
    driver: WebDriver, timeout: int = 30
) -> Optional[WebElement]:
    return WebDriverWait(driver, timeout).until(
        presence_of_element_located(AD_DETAILS_CONTENT)
    )


@return_on_failure(WebDriverException)
def parse_ad_link(card: WebElement) -> Optional[str]:
    return card.find_element(*AD_LINK).get_attribute("href")


@return_on_failure(WebDriverException)
def parse_ad_title(card: WebElement) -> Optional[str]:
    return card.find_element(*AD_TITLE).text.strip()


@return_on_failure(WebDriverException)
def parse_ad_price(card: WebElement) -> Optional[str]:
    return card.find_element(*AD_PRICE).text.strip()


@return_on_failure(WebDriverException)
def parse_ad_location(card: WebElement) -> Optional[str]:
    return card.find_element(*AD_LOCATION).text.strip()


@return_on_failure(WebDriverException)
def parse_ad_details_title(content: WebElement) -> Optional[str]:
    text = content.find_element(*AD_DETAILS_TITLE).text.strip()
    text = text.replace('"', "'")
    return text


@return_on_failure(WebDriverException)
def parse_ad_details_description(content: WebElement) -> Optional[str]:
    text = content.find_element(*AD_DETAILS_DESCRIPTION).text.strip()
    text = text.replace('"', "'")
    text = "<br>".join(text.splitlines())
    return text


@return_on_failure(WebDriverException)
def parse_ad_details_price(content: WebElement) -> Optional[str]:
    return content.find_element(*AD_DETAILS_PRICE).text.strip()


@return_on_failure(WebDriverException)
def parse_ad_details_author(content: WebElement) -> Optional[str]:
    return content.find_element(*AD_DETAILS_AUTHOR).text.strip()


@return_on_failure(WebDriverException)
def parse_ad_details_profile(content: WebElement) -> Optional[str]:
    return content.find_element(*AD_DETAILS_PROFILE).get_attribute("href").strip()


@return_on_failure(WebDriverException)
def parse_ad_details_location(content: WebElement) -> Optional[str]:
    return content.find_element(*AD_DETAILS_LOCATION).get_attribute("alt").strip()


def parse_ad(card: WebElement, kind: str) -> Dict[str, Any]:
    item = {}

    add_field(item, "link", lambda: parse_ad_link(card))
    add_field(item, "kind", lambda: kind)
    add_field(item, "title", lambda: parse_ad_title(card))
    add_field(item, "price", lambda: parse_ad_price(card))
    add_field(item, "location", lambda: parse_ad_location(card))

    return item


@inject.autoparams("driver", "fieldnames")
def parse_ads(
    link: str,
    driver: WebDriver,
    exclude_free: bool = False,
    exclude_paid: bool = False,
) -> Generator[Dict[str, Any], None, None]:
    if exclude_free and exclude_paid:
        return

    try:
        driver.get(link)
    except WebDriverException:
        return

    free = map(lambda c: parse_ad(c, kind="free"), find_free_ads(exclude_free))
    paid = map(lambda c: parse_ad(c, kind="paid"), find_paid_ads(exclude_paid))

    for ad in filter(lambda a: a is not None, chain(free, paid)):
        yield ad

    next_page = find_next_ads_page()
    if next_page is not None:
        yield from parse_ads(
            next_page, exclude_free=exclude_free, exclude_paid=exclude_paid
        )


@inject.autoparams("driver")
def parse_ad_details(link: str, driver: WebDriver) -> Optional[Dict[str, Any]]:
    try:
        driver.get(link)
    except WebDriverException:
        return None

    content = find_ad_details_content()
    if content is None:
        return None

    fields = {}

    add_field(fields, "link", lambda: link)
    add_field(fields, "title", lambda: parse_ad_details_title(content))
    add_field(fields, "description", lambda: parse_ad_details_description(content))
    add_field(fields, "price", lambda: parse_ad_details_price(content))
    add_field(fields, "author", lambda: parse_ad_details_author(content))
    add_field(fields, "profile", lambda: parse_ad_details_profile(content))
    add_field(fields, "location", lambda: parse_ad_details_location(content))

    return fields


# ------------------------------------------------------------------------------------ #
# Common arguments & options
# ------------------------------------------------------------------------------------ #

links = click.argument("links", nargs=-1, type=click.STRING, metavar="[LINK]")

headless = click.option(
    "--headless/--no-headless",
    is_flag=True,
    default=True,
    help="Enable / disable headless mode for browser.",
)
progress = click.option("--progress", is_flag=True, help="Enable progressbar.")
proxy = click.option("--proxy", type=click.STRING, help="Proxy server.")
link = click.option(
    "--link/--no-link", is_flag=True, default=True, help="Collect / skip link."
)

title = click.option("--title", is_flag=True, help="Collect title.")
price = click.option("--price", is_flag=True, help="Collect price.")
location = click.option("--location", is_flag=True, help="Collect location.")
all = click.option("--all", is_flag=True, help="Collect all fields.")

# ------------------------------------------------------------------------------------ #


@click.group()
def cli():
    """
    An easy-to-use, powerful crawler for OLX, that allows collecting various
    non-sensitivity data about ads on the site.
    """

    pass


@cli.command()
@links
@progress
@headless
@proxy
@link
@click.option("--kind", is_flag=True, help="Collect kind (free or paid).")
@title
@price
@location
@all
def ads(
    links: Tuple[str, ...],
    headless: bool,
    progress: bool,
    proxy: Optional[str],
    all: bool,
    **kwargs,
):
    """
    Collects minimal data about each ad. Use flag-like options to collect only required
    fields. For more detailed data use another command.
    """

    links = get_links(links, progress)

    with chrome(headless, proxy) as driver:

        def config(binder: inject.Binder):
            binder.bind(WebDriver, driver)
            binder.bind(Set[str], create_fieldnames(kwargs, all))

        inject.configure(config)

        writer = csv_writer()
        next(writer)

        for link in links:
            for item in parse_ads(link):
                writer.send(item)


@cli.command()
@links
@progress
@headless
@proxy
@link
@title
@click.option("--description", is_flag=True, help="Collect description.")
@click.option("--author", is_flag=True, help="Collect author.")
@click.option("--profile", is_flag=True, help="Collect author's profile link.")
@price
@location
@all
@click.option(
    "--keywords",
    type=click.File("r", encoding="utf-8"),
    help="File with keywords line by line.",
)
def ad(
    links: Tuple[str, ...],
    headless: bool,
    progress: bool,
    proxy: Optional[str],
    all: bool,
    keywords: Optional[TextIO],
    **kwargs,
):
    """
    Collects details about ad. Use flag-like options to collect only required fields.
    Also, the command supports basic ad filtering by keywords. The command uses the
    Aho-Corasick algorithm for keywords search. In the search process are involved
    title and description fields. To specify keywords, use a file with keywords line by
    line.
    """

    links = get_links(links, progress)

    keywords_tree = create_keywords_tree(keywords) if keywords else None
    if keywords_tree:
        kwargs.update(dict(title=True, description=True))

    fieldnames = create_fieldnames(kwargs, all)

    with chrome(headless, proxy) as driver:

        def config(binder: inject.Binder):
            binder.bind(WebDriver, driver)
            binder.bind(Set[str], fieldnames)

        inject.configure(config)

        writer = csv_writer()
        next(writer)

        for link in links:
            item = parse_ad_details(link)
            if keywords is None or has_keywords(item, keywords_tree):
                writer.send(item)


if __name__ == "__main__":
    cli()
