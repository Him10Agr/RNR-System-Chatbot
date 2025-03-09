from urllib.parse import urlparse

from loguru import logger
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import get_step_context, step

from llm.application.crawlers import HTMLCrawler


@step
def crawl_links(links: list[str]) -> Annotated[list[str], "crawled_links"]:
    crawler = HTMLCrawler()

    logger.info(f"Starting to crawl {len(links)} link(s).")

    metadata = {}
    successfull_crawls = 0
    for link in tqdm(links):
        successfull_crawl, crawled_path = _crawl_link(crawler, link)
        successfull_crawls += successfull_crawl

        metadata = _add_to_metadata(metadata, crawled_path, successfull_crawl)

    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_links", metadata=metadata)

    logger.info(f"Successfully crawled {successfull_crawls} / {len(links)} links.")

    return links


def _crawl_link(crawler: HTMLCrawler, link: str) -> tuple[bool, str]:
    crawler_path = urlparse(link).path

    try:
        crawler.extract(link=link)

        return (True, crawler_path)
    except Exception as e:
        logger.error(f"An error occurred while crawling: {e!s}")

        return (False, crawler_path)


def _add_to_metadata(metadata: dict, path: str, successfull_crawl: bool) -> dict:
    if path not in metadata:
        metadata[path] = {}
    metadata[path]["successful"] = metadata[path].get("successful", 0) + successfull_crawl
    metadata[path]["total"] = metadata[path].get("total", 0) + 1

    return metadata