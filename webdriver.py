#!/usr/bin/env python3

import contextlib
from typing import Iterator

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


@contextlib.contextmanager
def get_firefox_webdriver(*, headless: bool) -> Iterator[Firefox]:
    service = Service()
    options = Options()
    if headless:
        options.add_argument("-headless")
    driver = Firefox(
        service=service,
        options=options,
    )
    try:
        yield driver
    finally:
        driver.quit()
