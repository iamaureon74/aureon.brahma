# seo — brahma

`site.usel.json` describes this site for **usel 0.2**, the international SEO
compiler in `usel/` (python 3.11+, standard library only for a JSON spec).
usel writes `robots.txt`, `sitemap.xml` and the IndexNow key file into `apps/brahma-web/`.

## regenerate and check

```bash
cd seo/usel
python -m usel compile ../site.usel.json --output ../../apps/brahma-web --reports ../reports
python -m usel check-site ../../apps/brahma-web --base-url https://brahma.asherin.com
python -m pytest -q        # the compiler's own tests (needs pytest, PyYAML, fastapi, httpx)
```

`seo/reports/` holds the engine-by-engine guide, the 250-market coverage table,
the manifest and the IndexNow plan. they describe the plan, not the site, so
they are kept out of `apps/brahma-web/`.

## tell search engines about changes (IndexNow)

Bing, Yandex, Seznam, Naver and the other IndexNow participants accept change
notifications. after a deploy, once `https://brahma.asherin.com/<key>.txt` is live:

```bash
cd seo/usel
python -m usel submit-indexnow --sitemap ../../apps/brahma-web/sitemap.xml --key <indexnow_key from site.usel.json> --host https://brahma.asherin.com           # dry run
python -m usel submit-indexnow --sitemap ../../apps/brahma-web/sitemap.xml --key <indexnow_key from site.usel.json> --host https://brahma.asherin.com --execute
```

nothing is ever sent without `--execute`. Google does not take IndexNow; it reads
the sitemap named in `robots.txt`.

## what it does not do

it does not guarantee indexing or rankings, translate content, or contact any
search engine unless you run `submit-indexnow --execute`. see `usel/README.md`.
