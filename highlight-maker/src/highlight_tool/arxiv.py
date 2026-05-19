from __future__ import annotations

import re
import urllib3
from dataclasses import dataclass
from urllib.parse import urlparse

import requests


ARXIV_ID_RE = re.compile(r"(?P<id>\d{4}\.\d{4,5}(?:v\d+)?)")


@dataclass(frozen=True)
class ArxivSource:
    identifier: str
    pdf_url: str
    abs_url: str


def parse_arxiv_source(value: str) -> ArxivSource:
    match = ARXIV_ID_RE.search(value)
    if not match:
        raise ValueError(f"Could not find an arXiv identifier in: {value}")

    identifier = match.group("id")
    parsed = urlparse(value)

    if parsed.netloc and "arxiv.org" in parsed.netloc:
        pdf_url = f"https://arxiv.org/pdf/{identifier}"
        abs_url = f"https://arxiv.org/abs/{identifier}"
    else:
        pdf_url = f"https://arxiv.org/pdf/{identifier}"
        abs_url = f"https://arxiv.org/abs/{identifier}"

    return ArxivSource(identifier=identifier, pdf_url=pdf_url, abs_url=abs_url)


def download_pdf(source: ArxivSource, destination, verify_tls: bool = True) -> None:
    if not verify_tls:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(source.pdf_url, timeout=60, verify=verify_tls)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "pdf" not in content_type.lower() and not response.content.startswith(b"%PDF"):
        raise ValueError(f"Downloaded content does not look like a PDF: {content_type}")
    destination.write_bytes(response.content)
