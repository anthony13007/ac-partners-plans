#!/usr/bin/env python3
"""Fetch a villa listing (Airbnb first, any site as fallback) and return a normalised JSON.

  python3 fetch_listing.py <url>            # prints JSON
  python3 fetch_listing.py <url> -o x.json  # saves it

Airbnb: the SSR HTML embeds the whole photo tour ("accessibilityLabel" + "baseUrl"),
the sharing title (bedrooms / beds / baths / rating), personCapacity, amenities and
the description. Prices are NOT in the SSR HTML (loaded by XHR) -> pass --adr to villa.py.
Works from a normal computer; Airbnb blocks cloud IPs.
"""
import re, json, sys, html as H, urllib.request, urllib.parse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.5 Safari/605.1.15")

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def _clean(html):
    return html.replace("\\u002F", "/").replace("\\/", "/")

def _unescape_json_str(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s

def _text(htmltext):
    t = _unescape_json_str(htmltext)
    t = re.sub(r"<br\s*/?>|</p>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    return H.unescape(t).strip()

def parse_airbnb(html, url):
    c = _clean(html)
    m = re.search(r"/rooms/(\d+)", url)
    listing_id = m.group(1) if m else None
    out = {"source": "airbnb", "url": url, "listing_id": listing_id}

    # photos, in photo-tour order, with room labels
    pairs = re.findall(r'"accessibilityLabel":"([^"]*)","baseUrl":"(https://a0\.muscache\.com/im/pictures/(?:[a-z-]+/)?Hosting-[A-Za-z0-9%=\-]+/original/[0-9a-f-]{36}\.jpe?g)', c)
    seen, photos = set(), []
    for label, base in pairs:
        if base in seen: continue
        seen.add(base)
        photos.append({"label": label, "url": base + "?im_w=1440", "url_hd": base + "?im_w=1920", "id": base.rsplit("/", 1)[1]})
    if not photos:  # older layout: no labels, just URLs
        for base in re.findall(r'https://a0\.muscache\.com/im/pictures/(?:[a-z-]+/)?Hosting-[A-Za-z0-9%=\-]+/original/[0-9a-f-]{36}\.jpe?g', c):
            if base in seen: continue
            seen.add(base); photos.append({"label": "", "url": base + "?im_w=1440", "url_hd": base + "?im_w=1920", "id": base.rsplit("/", 1)[1]})
    out["photos"] = photos

    # title / city
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    title = H.unescape(t.group(1)).strip() if t else ""
    title = re.sub(r"\s*-\s*Airbnb\s*$", "", title)
    m = re.search(r"^(.*?)\s*-\s*(?:Houses|Villas|Homes|[A-Za-z ]+) for Rent in (.+)$", title)
    if m:
        out["title"] = m.group(1).strip(" -"); out["location"] = m.group(2).strip()
    else:
        out["title"] = title; out["location"] = ""
    # sharing title: "Home in Kuta Utara · ★5.0 · 7 bedrooms · 10 beds · 6 baths"
    m = re.search(r'"sharingConfig":\{[^}]*?"title":"([^"]+)"', c)
    share = H.unescape(m.group(1)) if m else ""
    out["share_title"] = share
    m = re.search(r"in ([^·]+?)\s*·", share);           out["city"] = m.group(1).strip() if m else out["location"].split(",")[0].strip()
    m = re.search(r"★([\d.]+)", share);                 out["rating"] = float(m.group(1)) if m else None
    m = re.search(r"(\d+)\s*bedrooms?", share);         out["bedrooms"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+)\s*beds?\b", share);           out["beds"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+(?:\.\d+)?)\s*bath", share);    out["baths"] = float(m.group(1)) if m else None
    m = re.search(r'"personCapacity":(\d+)', c);        out["guests"] = int(m.group(1)) if m else None
    m = re.search(r'"(\d+) reviews?"', c);              out["reviews"] = int(m.group(1)) if m else None
    out["superhost"] = '"isSuperhost":true' in c

    # description = longest htmlText block on the page
    cands = sorted(set(re.findall(r'"htmlText":"((?:[^"\\]|\\.)*)"', c)), key=len, reverse=True)
    out["description"] = _text(cands[0]) if cands else ""
    # amenities (available ones)
    am, seen = [], set()
    for a in re.findall(r'"available":true,"title":"([^"]{2,50})"', c):
        a = H.unescape(a)
        if a not in seen: seen.add(a); am.append(a)
    out["amenities"] = am
    return out

def parse_generic(html, url):
    c = _clean(html)
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(url))
    urls = re.findall(r'https?://[^\s"\'<>)]+?\.(?:jpe?g|webp|png)(?:\?[^\s"\'<>)]*)?', c, re.I)
    urls += [base + u for u in re.findall(r'"(/[^\s"\'<>]+?\.(?:jpe?g|webp)(?:\?[^\s"\'<>]*)?)"', c, re.I)]
    bad = ("logo", "icon", "favicon", "sprite", "avatar", "flag", "badge", "amenit", "platform-assets", "platformassets")
    seen, photos = set(), []
    for u in urls:
        key = u.split("?")[0]
        if key in seen or any(b in u.lower() for b in bad): continue
        seen.add(key); photos.append({"label": "", "url": u, "url_hd": u, "id": key.rsplit("/", 1)[-1]})
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    d = re.search(r'name="description" content="([^"]*)"', html)
    out = {"source": "site", "url": url, "title": H.unescape(t.group(1)).strip() if t else "", "description": H.unescape(d.group(1)) if d else "",
           "photos": photos, "city": "", "location": "", "amenities": []}
    m = re.search(r"(\d+)\s*[- ]?(?:bed(?:room)?s?|BR)\b", html, re.I); out["bedrooms"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+)\s*guests?", html, re.I);               out["guests"] = int(m.group(1)) if m else None
    return out

def fetch_listing(url, tries=5):
    """Airbnb serves a lighter shell (no photo tour) at random: retry until the photos are there."""
    import time
    if "airbnb." in url:
        url = re.sub(r"\?.*$", "", url)  # strip search params, they change the SSR variant
        best = None
        for i in range(tries):
            d = parse_airbnb(fetch(url), url)
            if d["photos"] and (best is None or len(d["photos"]) > len(best["photos"])): best = d
            if best and len(best["photos"]) >= 20: break
            time.sleep(1.5)
        return best or d
    return parse_generic(fetch(url), url)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("url"); ap.add_argument("-o", "--out")
    a = ap.parse_args()
    d = fetch_listing(a.url)
    s = json.dumps(d, ensure_ascii=False, indent=1)
    if a.out: open(a.out, "w", encoding="utf-8").write(s); print("saved", a.out, "photos:", len(d["photos"]))
    else: print(s)
