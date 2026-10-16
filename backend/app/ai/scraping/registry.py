from typing import Any

from app.ai.scraping.base import BaseProductScraper
from app.ai.scraping.sources.gypsobat import GypsobatScraper
from app.ai.scraping.sources.emtop import EmtopScraper
from app.ai.scraping.sources.sofap import SofapScraper


_scrapers: dict[str, BaseProductScraper] = {}


def register_scraper(scraper: BaseProductScraper) -> None:
    _scrapers[scraper.source] = scraper


def get_scraper(source: str) -> BaseProductScraper:
    return _scrapers[source]


def list_sources() -> list[str]:
    return list(_scrapers.keys())


register_scraper(GypsobatScraper())
register_scraper(EmtopScraper())
register_scraper(SofapScraper())
