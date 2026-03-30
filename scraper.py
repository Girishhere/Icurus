"""
scraper.py - Data Pipeline for Icurus
Fetches coding problems from the web or returns a hardcoded fallback.
"""

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

FALLBACK_PROBLEM = {
    "problem": "Write a Python function to check if a string is a palindrome.",
    "tests": [
        {"input": "racecar", "expected": "True"},
        {"input": "hello",   "expected": "False"},
    ],
}


def fetch_problem_data(url: str = "") -> dict:
    """
    Attempts to scrape a coding problem from the given URL.
    Falls back to a hardcoded palindrome problem if anything goes wrong.
    """
    try:
        if not url:
            raise ValueError("No URL provided – using fallback problem.")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Generic extraction – works for simple problem pages
        title_tag = soup.find("h1") or soup.find("h2")
        paragraphs = soup.find_all("p")
        body = " ".join(p.get_text(strip=True) for p in paragraphs[:3])

        problem_text = (
            f"{title_tag.get_text(strip=True)}: {body}"
            if title_tag
            else body
        )

        if not problem_text.strip():
            raise ValueError("Could not extract problem text from page.")

        return {
            "problem": problem_text,
            "tests": [
                {"input": "sample_input", "expected": "sample_output"},
            ],
        }

    except Exception:
        # Always return a working fallback so the demo never crashes
        return FALLBACK_PROBLEM
