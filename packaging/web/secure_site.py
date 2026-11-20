"""Externalize inline scripts and styles before publishing the static site.

Keep script order and module attributes; content hashes make immutable caching safe.
No application JavaScript is authored here: the existing loader is moved verbatim.
"""

import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


class ScriptTag(HTMLParser):
    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def secure_site(site):
    page = site / "index.html"
    html = page.read_text(encoding="utf-8")

    def externalize(match):
        opening, body = match.groups()
        parser = ScriptTag()
        parser.feed(opening)
        attrs = parser.attrs
        if "src" in attrs:
            return match.group(0)
        if attrs.get("type", "").lower() not in ("", "module", "text/javascript", "application/javascript"):
            return match.group(0)
        content = body.encode("utf-8")
        digest = hashlib.sha256(content).digest()
        name = "startup-" + digest.hex() + ".js"
        (site / name).write_bytes(content)
        integrity = base64.b64encode(digest).decode("ascii")
        return opening[:-1] + f' src="./{name}" integrity="sha256-{integrity}"></script>'

    html = re.sub(r"(<script\b[^>]*>)(.*?)</script\s*>", externalize, html, flags=re.I | re.S)

    def externalize_style(match):
        content = match.group(1).encode("utf-8")
        digest = hashlib.sha256(content).digest()
        name = "style-" + digest.hex() + ".css"
        (site / name).write_bytes(content)
        integrity = base64.b64encode(digest).decode("ascii")
        return f'<link rel="stylesheet" href="./{name}" integrity="sha256-{integrity}">'

    html = re.sub(r"<style\s*>(.*?)</style\s*>", externalize_style, html, flags=re.I | re.S)
    page.write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    secure_site(Path(sys.argv[1]))
