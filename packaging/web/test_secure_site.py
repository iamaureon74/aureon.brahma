"""Run with python -m unittest discover -s packaging/web -p 'test_*.py'."""

import base64
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

from secure_site import secure_site

ROOT = Path(__file__).resolve().parents[2]


class SecurityTests(unittest.TestCase):
    def test_externalizes_page_and_trunk_loader_preserving_bytes_order_and_type(self):
        source = (ROOT / "apps/brahma-web/index.html").read_text(encoding="utf-8")
        source += '<script type="module">import init from "./app.js"; await init();</script>'
        bodies = re.findall(r"<script\b[^>]*>(.*?)</script>", source, re.S)
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            page = site / "index.html"
            page.write_text(source, encoding="utf-8")
            secure_site(site)
            result = page.read_text(encoding="utf-8")
            tags = re.findall(r'<script\b[^>]*src="\./([^"]+)"[^>]*></script>', result)
            self.assertEqual(len(tags), 2)
            for name, body in zip(tags, bodies):
                content = (site / name).read_bytes()
                self.assertEqual(content, body.encode("utf-8"))
                digest = base64.b64encode(hashlib.sha256(content).digest()).decode()
                self.assertIn(f'integrity="sha256-{digest}"', result)
            self.assertIn('<script type="module" src=', result)
            self.assertNotIn("<style>", result)
            css = re.search(r'<link rel="stylesheet" href="\./([^"]+)" integrity="([^"]+)"', result)
            self.assertIsNotNone(css)
            content = (site / css.group(1)).read_bytes()
            self.assertEqual(content, re.search(r"<style>(.*?)</style>", source, re.S).group(1).encode("utf-8"))
            self.assertEqual(css.group(2), "sha256-" + base64.b64encode(hashlib.sha256(content).digest()).decode())
            secure_site(site)
            self.assertEqual(page.read_text(encoding="utf-8"), result)

    def test_leaves_external_scripts_and_inert_data_alone(self):
        source = '<script src="app.js"></script><script type="application/json">{"x":1}</script>'
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "index.html").write_text(source)
            secure_site(site)
            self.assertEqual((site / "index.html").read_text(), source)

    def test_hosting_policy_and_build_entry_points(self):
        config = json.loads((ROOT / "vercel.json").read_text())
        headers = {h["key"].lower(): h["value"] for h in config["headers"][0]["headers"]}
        csp = headers["content-security-policy"]
        scripts = next(d for d in csp.split(";") if d.strip().startswith("script-src "))
        self.assertNotIn("'unsafe-inline'", csp)
        self.assertIn("style-src 'self'", csp)
        self.assertIn("'wasm-unsafe-eval'", scripts)
        self.assertIn("frame-ancestors 'self'", csp)
        # The Ollama and LM Studio presets talk to a server on this computer over plain http.
        connect = next(d for d in csp.split(";") if d.strip().startswith("connect-src "))
        self.assertIn("http://localhost:*", connect)
        self.assertNotIn("upgrade-insecure-requests", csp)
        self.assertEqual(headers["x-frame-options"], "SAMEORIGIN")
        self.assertIn("includeSubDomains", headers["strict-transport-security"])
        for name in ("cross-origin-opener-policy", "cross-origin-resource-policy"):
            self.assertEqual(headers[name], "same-origin")
        self.assertEqual(headers["access-control-allow-origin"], "https://brahma.asherin.com")
        for name in ("package.sh", "vercel-build.sh"):
            self.assertIn('secure_site.py" "$SITE"', (ROOT / "packaging/web" / name).read_text())


if __name__ == "__main__":
    unittest.main()
