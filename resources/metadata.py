import html
import json
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


class MetadataError(ValueError):
    pass


def _fetch_page(url):
    try:
        response = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; JobTrackerResources/1.0; "
                    "+https://jobtracker.local)"
                ),
            },
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise MetadataError("Could not read metadata from this URL.") from exc

    return response.text


def _first_meta_content(soup, selectors):
    for attrs in selectors:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return tag["content"].strip()

    return ""


def _canonical_url(soup, fallback_url):
    tag = soup.find("link", rel=lambda value: value and "canonical" in value)

    if tag and tag.get("href"):
        return tag["href"].strip()

    return fallback_url


def _domain_source_name(url):
    hostname = urlparse(url).hostname or ""
    return hostname.removeprefix("www.")


def _parse_publication_date(value):
    if not value:
        return None

    try:
        parsed = date_parser.parse(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return parsed.date()


def _title_from_page(soup):
    title = _first_meta_content(
        soup,
        [
            {"property": "og:title"},
            {"name": "twitter:title"},
            {"name": "title"},
        ],
    )

    if title:
        return title

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return ""


def _is_chatgpt_share_url(url):
    parsed_url = urlparse(url)
    hostname = (parsed_url.hostname or "").removeprefix("www.")

    return hostname in {"chatgpt.com", "chat.openai.com"} and "/share/" in parsed_url.path


def _message_text_from_content(content):
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        return "\n".join(
            text for text in (_message_text_from_content(item) for item in content) if text
        ).strip()

    if not isinstance(content, dict):
        return ""

    if isinstance(content.get("text"), str):
        return content["text"].strip()

    if isinstance(content.get("parts"), list):
        return _message_text_from_content(content["parts"])

    if isinstance(content.get("content"), (dict, list, str)):
        return _message_text_from_content(content["content"])

    return ""


def _message_from_object(value):
    if not isinstance(value, dict):
        return None

    role = ""
    author = value.get("author")

    if isinstance(author, dict):
        role = author.get("role", "")

    role = role or value.get("role", "")

    if role not in {"user", "assistant"}:
        return None

    text = _message_text_from_content(value.get("content"))

    if not text:
        return None

    return {"role": role, "text": text}


def _collect_messages(value, messages):
    message = _message_from_object(value)

    if message:
        messages.append(message)

    if isinstance(value, dict):
        for child in value.values():
            _collect_messages(child, messages)
    elif isinstance(value, list):
        for child in value:
            _collect_messages(child, messages)


def _json_objects_from_script(script_text):
    text = html.unescape(script_text or "").strip()

    if not text:
        return []

    objects = []
    decoder = json.JSONDecoder()

    if text.startswith(("{", "[")):
        try:
            objects.append(json.loads(text))
            return objects
        except json.JSONDecodeError:
            pass

    for match in re.finditer(r"[{\[]", text):
        try:
            parsed, _ = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue

        objects.append(parsed)

        if len(objects) >= 8:
            break

    return objects


def _extract_chatgpt_messages(soup):
    messages = []

    for script in soup.find_all("script"):
        script_text = script.string or script.get_text()

        for parsed in _json_objects_from_script(script_text):
            _collect_messages(parsed, messages)

    deduped = []
    seen = set()

    for message in messages:
        key = (message["role"], message["text"])

        if key in seen:
            continue

        seen.add(key)
        deduped.append(message)

    return deduped


def _latest_question_answer(messages):
    for index in range(len(messages) - 1, -1, -1):
        if messages[index]["role"] != "assistant":
            continue

        for previous_index in range(index - 1, -1, -1):
            if messages[previous_index]["role"] == "user":
                return messages[previous_index]["text"], messages[index]["text"]

    return "", ""


def extract_chatgpt_shared_metadata(url):
    if not _is_chatgpt_share_url(url):
        raise MetadataError("Please use a public ChatGPT shared conversation URL.")

    html_text = _fetch_page(url)
    soup = BeautifulSoup(html_text, "html.parser")
    messages = _extract_chatgpt_messages(soup)
    question, answer = _latest_question_answer(messages)

    if not question or not answer:
        raise MetadataError(
            "Could not read this ChatGPT shared conversation. Paste the question and answer manually."
        )

    title = _title_from_page(soup)
    title = title.replace("ChatGPT - ", "").replace("ChatGPT", "").strip()

    return {
        "title": title or question[:90] or "ChatGPT answer",
        "source_name": "ChatGPT",
        "url": _canonical_url(soup, url),
        "question": question,
        "answer": answer,
    }


def extract_url_metadata(url):
    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        raise MetadataError("Please use an http or https URL.")

    soup = BeautifulSoup(_fetch_page(url), "html.parser")
    title = _title_from_page(soup)
    source_name = _first_meta_content(
        soup,
        [
            {"property": "og:site_name"},
            {"name": "application-name"},
            {"name": "twitter:site"},
        ],
    )
    author = _first_meta_content(
        soup,
        [
            {"name": "author"},
            {"property": "article:author"},
            {"name": "parsely-author"},
            {"name": "byl"},
        ],
    )
    published_value = _first_meta_content(
        soup,
        [
            {"property": "article:published_time"},
            {"name": "date"},
            {"name": "pubdate"},
            {"name": "publishdate"},
            {"name": "datePublished"},
            {"itemprop": "datePublished"},
        ],
    )
    published_at = _parse_publication_date(published_value)
    canonical_url = _canonical_url(soup, url)

    return {
        "title": title or canonical_url,
        "source_name": source_name or _domain_source_name(canonical_url),
        "author": author,
        "published_at": published_at.isoformat() if published_at else None,
        "url": canonical_url,
    }
