#!/usr/bin/env python3
"""26.3Q 미국DB에서 캘린더 종목의 Notion Transcript 페이지를 수집합니다."""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR_FILE = os.path.join(ROOT, "data", "calendar.json")
OUTPUT_FILE = os.path.join(ROOT, "data", "notion-transcripts.json")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
NOTION_DATABASE_ID = os.environ.get(
    "NOTION_DATABASE_ID",
    "0850296c-0da5-4d53-b3a6-2bf62ab932e0",
).strip()
NOTION_DATA_SOURCE_ID = os.environ.get(
    "NOTION_DATA_SOURCE_ID",
    "6df7fb69-2624-4a66-92e8-1e03afeea1ba",
).strip()
NOTION_VERSION = "2026-03-11"
NOTION_API = "https://api.notion.com/v1"


def read_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return fallback
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON 형식 오류: {path}\n{exc}") from exc


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def notion_request(method, endpoint, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{NOTION_API}{endpoint}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Notion API 오류: HTTP {exc.code}\n{detail}"
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Notion 연결 실패: {exc}") from exc


def page_title(page):
    for prop in page.get("properties", {}).values():
        if prop.get("type") != "title":
            continue
        return "".join(
            item.get("plain_text", "")
            for item in prop.get("title", [])
        ).strip()
    return ""


def collect_valid_tickers():
    data = read_json(CALENDAR_FILE, {"entries": []})
    entries = data.get("entries", [])
    tickers = {
        str(item.get("ticker", "")).upper().strip()
        for item in entries
        if isinstance(item, dict) and item.get("ticker")
    }
    if not tickers:
        raise RuntimeError("calendar.json에서 티커를 찾지 못했습니다.")
    return tickers


def query_pages():
    pages = []
    cursor = None

    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor

        response = notion_request(
            "POST",
            f"/data_sources/{NOTION_DATA_SOURCE_ID}/query",
            payload,
        )
        pages.extend(response.get("results", []))

        if not response.get("has_more"):
            return pages

        cursor = response.get("next_cursor")
        if not cursor:
            return pages
        time.sleep(0.2)


def collect_transcript_links(valid_tickers):
    matched = {}

    for page in query_pages():
        title = page_title(page)
        match = re.match(
            r"^\s*([A-Z][A-Z0-9.\-]{0,9})\s*[-–—]\s*",
            title.upper(),
        )
        if not match:
            continue

        ticker = match.group(1)
        url = page.get("url")
        if ticker not in valid_tickers or not url:
            continue

        edited = page.get("last_edited_time", "")
        previous = matched.get(ticker)
        if previous is None or edited > previous["edited"]:
            matched[ticker] = {"url": url, "edited": edited}

    return {
        ticker: item["url"]
        for ticker, item in sorted(matched.items())
    }


def main():
    if not NOTION_TOKEN:
        raise RuntimeError(
            "GitHub Actions Secret NOTION_TOKEN이 없습니다. "
            "26.3Q 미국DB를 공유한 Notion Integration 토큰을 추가하세요."
        )

    links = collect_transcript_links(collect_valid_tickers())
    previous = read_json(OUTPUT_FILE, {})
    if links == previous.get("links", {}):
        print("변경된 Transcript 링크가 없습니다.")
        return

    kst = timezone(timedelta(hours=9))
    output = {
        "source": "Notion 26.3Q 미국DB",
        "databaseId": NOTION_DATABASE_ID,
        "dataSourceId": NOTION_DATA_SOURCE_ID,
        "updated": datetime.now(kst).strftime("%Y-%m-%d %H:%M KST"),
        "links": links,
    }
    write_json(OUTPUT_FILE, output)
    print(f"Transcript 링크 {len(links)}개를 갱신했습니다.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"실행 실패: {exc}", file=sys.stderr)
        sys.exit(1)
