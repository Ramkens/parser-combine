"""GitHub trending repositories parser (HTML scrape, no auth)."""
from __future__ import annotations

from typing import Any, AsyncIterator, Dict

from selectolax.parser import HTMLParser

from app.core.logger import get_logger
from app.parsers.base import BaseParser, ParseTask

log = get_logger("parser.github")


class GitHubTrendingParser(BaseParser):
    name = "github"
    columns = ["repo", "url", "language", "stars", "forks", "description"]

    def fetch(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        return self._iter(task)

    async def _iter(self, task: ParseTask) -> AsyncIterator[Dict[str, Any]]:
        produced = 0
        ranges = task.opt("ranges") or ["daily", "weekly", "monthly"]
        languages = task.opt("languages") or [""]
        kw = [k.lower() for k in (task.keywords or []) if k.strip()]
        for since in ranges:
            for lang in languages:
                if produced >= task.limit:
                    break
                params = {"since": since}
                if lang:
                    params["spoken_language_code"] = lang
                url = "https://github.com/trending"
                if lang and lang.lower() not in ("ru", "en"):
                    # treat lang as a programming language
                    url = f"https://github.com/trending/{lang}"
                    params = {"since": since}
                try:
                    html = await self.http.get(url, params=params)
                except Exception as e:
                    log.warning("github trending %s/%s failed: %s", since, lang, e)
                    continue
                tree = HTMLParser(html)
                for art in tree.css("article.Box-row"):
                    if produced >= task.limit:
                        break
                    a = art.css_first("h2 a")
                    repo = (a.text(strip=True).replace(" ", "").replace("\n", "")) if a else ""
                    href = ("https://github.com" + a.attributes.get("href", "")) if a else ""
                    desc_node = art.css_first("p")
                    desc = desc_node.text(strip=True) if desc_node else ""
                    if kw and not any(k in (repo + " " + desc).lower() for k in kw):
                        continue
                    lang_node = art.css_first("span[itemprop='programmingLanguage']")
                    stars_nodes = art.css("a.Link--muted")
                    stars = stars_nodes[0].text(strip=True) if len(stars_nodes) > 0 else ""
                    forks = stars_nodes[1].text(strip=True) if len(stars_nodes) > 1 else ""
                    yield {
                        "repo": repo,
                        "url": href,
                        "language": lang_node.text(strip=True) if lang_node else "",
                        "stars": stars,
                        "forks": forks,
                        "description": desc,
                    }
                    produced += 1
