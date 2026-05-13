import abc
from typing import Any, Dict, List
from src.models import ProductVariantInput

class BaseAdapter(abc.ABC):
    """
    Abstract Base Class for all site-specific scrapers.
    """

    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url

    @abc.abstractmethod
    async def scrape(self) -> str:
        """
        Performs the actual web scraping (using Playwright or HTTPX).
        Returns the raw HTML or content of the page.
        """
        pass

    @abc.abstractmethod
    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parses the raw HTML content and extracts product information.
        Returns a list of dictionaries containing raw product data.
        """
        pass

    @abc.abstractmethod
    def validate(self, raw_data: Dict[str, Any]) -> ProductVariantInput:
        """
        Validates the raw dictionary data and converts it into a
        standardized ProductVariantInput object.
        """
        pass

    async def run(self) -> List[ProductVariantInput]:
        """
        The main execution pipeline: Scrape -> Parse -> Validate.
        """
        print(f"[{self.source_name}] Starting scrape...")
        html = await self.scrape()

        if not html:
            print(f"[{self.source_name}] Failed to retrieve content.")
            return []

        print(f"[{self.source_name}] Parsing content...")
        try:
            raw_products = self.parse(html)
        except Exception as e:
            print(f"[{self.source_name}] Parsing error: {e}")
            return []

        valid_products = []
        for item in raw_products:
            try:
                validated = self.validate(item)
                valid_products.append(validated)
            except Exception as e:
                print(f"[{self.source_name}] Validation error for item: {e}")

        print(f"...")
        print(f"[{self.source_name}] Successfully processed {len(valid_products)} products.")
        return valid_products
