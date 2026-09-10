#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════╗
# ║          EH WEB v3.1 — Deep Multi-Page Source Crawler           ║
# ║          Author : EH Munna 👿 @#9002111185000#                  ║
# ║          Mode   : Full Asset + Image Extraction                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import gzip
import time
import socket
import re
import json
import hashlib
import threading
from collections import deque
from html.parser import HTMLParser

# ════════════════════════════════════════════════════════════════════
#  ANSI — GREEN THEME
# ════════════════════════════════════════════════════════════════════
G1  = "\033[38;5;46m"
G2  = "\033[38;5;40m"
G3  = "\033[38;5;34m"
G4  = "\033[38;5;28m"
GD  = "\033[38;5;22m"
BG  = "\033[1;32m"
W   = "\033[1;37m"
DW  = "\033[0;37m"
DIM = "\033[2m"
RED = "\033[1;31m"
YEL = "\033[1;33m"
RS  = "\033[0m"

# ════════════════════════════════════════════════════════════════════
#  BANNER
# ════════════════════════════════════════════════════════════════════
def banner():
    os.system("clear")
    print(f"""
{G1}  ███████╗██╗  ██╗    ██╗    ██╗███████╗██████╗ {RS}
{G1}  ██╔════╝██║  ██║    ██║    ██║██╔════╝██╔══██╗{RS}
{G2}  █████╗  ███████║    ██║ █╗ ██║█████╗  ██████╔╝{RS}
{G2}  ██╔══╝  ██╔══██║    ██║███╗██║██╔══╝  ██╔══██╗{RS}
{G3}  ███████╗██║  ██║    ╚███╔███╔╝███████╗██████╔╝{RS}
{G3}  ╚══════╝╚═╝  ╚═╝     ╚══╝╚══╝ ╚══════╝╚═════╝ {RS}

{G2}  ╔══════════════════════════════════════════════════════╗{RS}
{G2}  ║  {W}Tool    : {G1}EH WEB — Deep Multi-Page Crawler    {G2}║{RS}
{G2}  ║  {W}Version : {G1}v3.1   {W}Mode: {G1}Source + Asset Extract {G2}║{RS}
{G2}  ║  {W}Author  : {G1}EH Munna 👿 @#9002111185000#        {G2}║{RS}
{G2}  ║  {W}Extracts: {G1}HTML·CSS·JS·IMG·SVG·PNG·FONT·BIN   {G2}║{RS}
{G2}  ╚══════════════════════════════════════════════════════╝{RS}
""")

# ════════════════════════════════════════════════════════════════════
#  STATUS HELPERS
# ════════════════════════════════════════════════════════════════════
def ok(msg):    print(f"  {G1}[+]{RS} {W}{msg}{RS}")
def info(msg):  print(f"  {G2}[*]{RS} {DW}{msg}{RS}")
def warn(msg):  print(f"  {YEL}[!]{RS} {DW}{msg}{RS}")
def err(msg):   print(f"  {RED}[✗]{RS} {DW}{msg}{RS}")
def step(msg):  print(f"  {G3}[→]{RS} {DW}{msg}{RS}")
def saved(msg): print(f"  {G1}[✔]{RS} {G2}{msg}{RS}")

def section(title):
    pad = max(0, 52 - len(title))
    print(f"\n{G2}  ╔══ {G1}{title}{G2} {'═'*pad}╗{RS}")

def section_end():
    print(f"{G2}  ╚{'═'*58}╝{RS}\n")

# ════════════════════════════════════════════════════════════════════
#  SPINNER
# ════════════════════════════════════════════════════════════════════
_spin_active = False
_spin_thread  = None

def _spin_worker(msg):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    while _spin_active:
        print(f"\r{G1}  {frames[i%len(frames)]}  {W}{msg}{RS}", end="", flush=True)
        time.sleep(0.08)
        i += 1
    print("\r"+" "*(len(msg)+10)+"\r", end="", flush=True)

def spin_start(msg):
    global _spin_active, _spin_thread
    _spin_active = True
    _spin_thread = threading.Thread(target=_spin_worker, args=(msg,), daemon=True)
    _spin_thread.start()

def spin_stop():
    global _spin_active
    _spin_active = False
    if _spin_thread:
        _spin_thread.join()

# ════════════════════════════════════════════════════════════════════
#  HEADERS
# ════════════════════════════════════════════════════════════════════
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.6367.82 Mobile Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control":   "no-cache",
    "DNT":             "1",
}

ASSET_HEADERS = dict(HEADERS)
ASSET_HEADERS["Accept"] = "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"

# ════════════════════════════════════════════════════════════════════
#  ASSET TYPE MAP
# ════════════════════════════════════════════════════════════════════
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp",
              ".avif", ".ico", ".bmp", ".tiff", ".tif"}
SVG_EXTS   = {".svg", ".svgz"}
FONT_EXTS  = {".woff", ".woff2", ".ttf", ".otf", ".eot"}
DOC_EXTS   = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
MEDIA_EXTS = {".mp4", ".webm", ".mp3", ".ogg", ".wav"}
SKIP_EXTS  = {".exe", ".dmg", ".apk", ".zip", ".tar", ".gz", ".rar"}
HTML_EXTS  = {"", ".html", ".htm", ".php", ".asp",
              ".aspx", ".jsp", ".cfm", ".cgi"}

def asset_category(url):
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if ext in IMAGE_EXTS:  return "images"
    if ext in SVG_EXTS:    return "svg"
    if ext in FONT_EXTS:   return "fonts"
    if ext in DOC_EXTS:    return "docs"
    if ext in MEDIA_EXTS:  return "media"
    if ext in SKIP_EXTS:   return None
    if ext == ".css":      return "css"
    if ext == ".js":       return "js"
    return None

def is_html_url(url):
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    return ext in HTML_EXTS

# ════════════════════════════════════════════════════════════════════
#  FETCH — TEXT
# ════════════════════════════════════════════════════════════════════
def raw_fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            enc = resp.headers.get("Content-Encoding", "")
            ct  = resp.headers.get("Content-Type", "")
            srv = resp.headers.get("Server", "Unknown")
            raw = resp.read()
            if enc == "gzip":
                try:    raw = gzip.decompress(raw)
                except: pass
            charset = "utf-8"
            if "charset=" in ct:
                charset = ct.split("charset=")[-1].split(";")[0].strip()
            try:    text = raw.decode(charset, errors="replace")
            except: text = raw.decode("utf-8",  errors="replace")
            return {
                "ok":     True,
                "text":   text,
                "raw":    raw,
                "status": resp.status,
                "url":    resp.geturl(),
                "ct":     ct,
                "server": srv,
            }
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code,  "error": str(e)}
    except urllib.error.URLError as e:
        return {"ok": False, "status": 0,       "error": str(e.reason)}
    except socket.timeout:
        return {"ok": False, "status": 0,       "error": "Timeout"}
    except Exception as e:
        return {"ok": False, "status": -1,      "error": str(e)}

# ════════════════════════════════════════════════════════════════════
#  FETCH — BINARY (images / fonts / docs)
# ════════════════════════════════════════════════════════════════════
def binary_fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=ASSET_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw  = resp.read()
            size = len(raw)
            ct   = resp.headers.get("Content-Type", "")
            return {"ok": True, "raw": raw, "size": size,
                    "status": resp.status, "ct": ct}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ════════════════════════════════════════════════════════════════════
#  HTML LINK PARSER
# ════════════════════════════════════════════════════════════════════
class LinkParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base       = base_url
        self.links      = set()
        self.css_links  = set()
        self.js_links   = set()
        self.img_links  = set()   # <img src>
        self.svg_links  = set()   # <img src=*.svg> / <use href>
        self.bg_links   = set()   # CSS url() in style attr
        self.srcset_links = set() # srcset
        self.forms      = []
        self._cur_form  = None

    def _abs(self, href):
        if not href:
            return None
        href = href.strip().split("#")[0]
        if href.startswith(("javascript:","mailto:","tel:",
                            "data:","blob:")):
            return None
        return urllib.parse.urljoin(self.base, href)

    def _parse_srcset(self, srcset):
        # "img.png 1x, img2x.png 2x"
        for part in srcset.split(","):
            url = part.strip().split()[0]
            u = self._abs(url)
            if u:
                yield u

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a":
            u = self._abs(d.get("href",""))
            if u: self.links.add(u)

        elif tag in ("img","image"):
            u = self._abs(d.get("src",""))
            if u:
                ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower()
                if ext in SVG_EXTS: self.svg_links.add(u)
                else:               self.img_links.add(u)
            ss = d.get("srcset","")
            if ss:
                for su in self._parse_srcset(ss):
                    self.srcset_links.add(su)

        elif tag == "picture":
            pass

        elif tag == "source":
            ss = d.get("srcset","")
            if ss:
                for su in self._parse_srcset(ss):
                    self.srcset_links.add(su)
            u = self._abs(d.get("src",""))
            if u: self.srcset_links.add(u)

        elif tag == "link":
            rel = d.get("rel","")
            u   = self._abs(d.get("href",""))
            if not u: return
            if "stylesheet" in rel:
                self.css_links.add(u)
            elif "icon" in rel or "apple-touch-icon" in rel:
                self.img_links.add(u)
            elif d.get("href","").endswith(tuple(SVG_EXTS)):
                self.svg_links.add(u)

        elif tag == "script":
            u = self._abs(d.get("src",""))
            if u: self.js_links.add(u)

        elif tag == "use":
            u = self._abs(d.get("href","") or d.get("xlink:href",""))
            if u: self.svg_links.add(u)

        elif tag == "object":
            u = self._abs(d.get("data",""))
            if u: self.img_links.add(u)

        elif tag == "embed":
            u = self._abs(d.get("src",""))
            if u: self.img_links.add(u)

        elif tag == "form":
            self._cur_form = {
                "action": d.get("action",""),
                "method": d.get("method","GET").upper(),
                "inputs": []
            }
        elif tag == "input" and self._cur_form is not None:
            self._cur_form["inputs"].append({
                "name": d.get("name",""),
                "type": d.get("type","text"),
                "id":   d.get("id",""),
            })

        # inline style background-image
        style = d.get("style","")
        if style and "url(" in style:
            for m in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)', style):
                u = self._abs(m.group(1))
                if u: self.bg_links.add(u)

    def handle_endtag(self, tag):
        if tag == "form" and self._cur_form is not None:
            self.forms.append(self._cur_form)
            self._cur_form = None

# ════════════════════════════════════════════════════════════════════
#  EXTRACT CSS url() REFERENCES
# ════════════════════════════════════════════════════════════════════
def extract_css_urls(css_text, base_url):
    urls = set()
    for m in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)', css_text):
        raw = m.group(1).strip()
        if raw.startswith("data:"): continue
        u = urllib.parse.urljoin(base_url, raw)
        urls.add(u)
    return urls

# ════════════════════════════════════════════════════════════════════
#  EXTRACT INLINE CSS / JS
# ════════════════════════════════════════════════════════════════════
def extract_inline(html):
    css = re.findall(r'<style[^>]*>(.*?)</style>',
                     html, re.DOTALL | re.IGNORECASE)
    js  = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>',
                     html, re.DOTALL | re.IGNORECASE)
    return css, js

# ════════════════════════════════════════════════════════════════════
#  SAFE FILENAME HELPERS
# ════════════════════════════════════════════════════════════════════
def url_to_filename(url, page_n=1):
    parsed = urllib.parse.urlparse(url)
    path   = parsed.path.strip("/")
    if not path:
        return "index.html"
    name = path.replace("/","_")
    name = re.sub(r'[^a-zA-Z0-9._\-]','_', name)
    if not any(name.endswith(e) for e in (".html",".htm",".php",".asp")):
        name += ".html"
    return name[:80]

def asset_safe_name(url):
    parsed = urllib.parse.urlparse(url)
    name   = os.path.basename(parsed.path)
    if not name:
        h    = hashlib.md5(url.encode()).hexdigest()[:8]
        ext  = os.path.splitext(parsed.path)[1] or ".bin"
        name = f"asset_{h}{ext}"
    name = re.sub(r'[^a-zA-Z0-9._\-]','_', name)
    return name[:80] or "unknown"

# ════════════════════════════════════════════════════════════════════
#  RESOLVE IP
# ════════════════════════════════════════════════════════════════════
def resolve_ip(url):
    try:
        host = urllib.parse.urlparse(url).hostname
        return socket.gethostbyname(host)
    except Exception:
        return "N/A"

# ════════════════════════════════════════════════════════════════════
#  PAGE TYPE LABEL
# ════════════════════════════════════════════════════════════════════
PAGE_TAGS = {
    "LOGIN":    ["login","signin","sign-in","log-in","auth"],
    "SIGNUP":   ["signup","register","sign-up","create-account","join"],
    "CONTACT":  ["contact","support","help"],
    "ABOUT":    ["about","team","company"],
    "CHECKOUT": ["checkout","cart","basket","order"],
    "SEARCH":   ["search","find","query"],
    "PROFILE":  ["profile","account","dashboard"],
    "ADMIN":    ["admin","panel","cpanel","wp-admin"],
    "BLOG":     ["blog","news","post","article"],
    "PRODUCT":  ["product","shop","store","item"],
    "GALLERY":  ["gallery","photo","portfolio","media"],
    "FAQ":      ["faq","help","questions"],
    "PRIVACY":  ["privacy","terms","policy","legal"],
}

def page_type(url):
    low = url.lower()
    for label, keys in PAGE_TAGS.items():
        if any(k in low for k in keys):
            return label
    return "PAGE"

# ════════════════════════════════════════════════════════════════════
#  OUTPUT FOLDER
# ════════════════════════════════════════════════════════════════════
def make_output_dir(base_url):
    parsed = urllib.parse.urlparse(base_url)
    domain = re.sub(r'[^a-zA-Z0-9_\-]','_',
                    parsed.netloc.replace("www.",""))
    ts     = time.strftime("%Y%m%d_%H%M%S")
    root   = f"EH_WEB_{domain}_{ts}"
    for sub in ("pages","css","js","images","svg",
                "fonts","docs","media","assets"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    return root

# ════════════════════════════════════════════════════════════════════
#  WRITE HELPERS
# ════════════════════════════════════════════════════════════════════
def write_text(folder, sub, name, content):
    p = os.path.join(folder, sub, name)
    with open(p, "w", encoding="utf-8", errors="replace") as f:
        f.write(content)
    return p

def write_binary(folder, sub, name, data):
    p = os.path.join(folder, sub, name)
    with open(p, "wb") as f:
        f.write(data)
    return p

# ════════════════════════════════════════════════════════════════════
#  PROGRESS BAR
# ════════════════════════════════════════════════════════════════════
def progress_bar(done, total, width=30):
    pct  = done / max(total, 1)
    fill = int(width * pct)
    bar  = "█" * fill + "░" * (width - fill)
    return f"{G1}[{bar}]{RS} {W}{done}/{total}{RS} {DIM}{pct*100:.0f}%{RS}"

# ════════════════════════════════════════════════════════════════════
#  BINARY ASSET DOWNLOADER
# ════════════════════════════════════════════════════════════════════
def download_assets(folder, asset_urls, manifest, delay=0.2):
    """
    asset_urls : set of (url, category)
    category   : images / svg / fonts / docs / media / assets
    """
    total   = len(asset_urls)
    done    = 0
    success = 0
    failed  = 0

    section(f"ASSET DOWNLOAD  ({total} files)")

    for url, cat in sorted(asset_urls, key=lambda x: x[1]):
        done += 1
        name = asset_safe_name(url)

        # avoid duplicates by checking if file exists
        dest = os.path.join(folder, cat, name)
        if os.path.exists(dest):
            step(f"Skip (exists) → {cat}/{name}")
            success += 1
            continue

        print(f"\r  {progress_bar(done, total)}  {DW}{name[:30]:<30}{RS}",
              end="", flush=True)

        res = binary_fetch(url, timeout=25)

        if res["ok"]:
            write_binary(folder, cat, name, res["raw"])
            size_s = (f"{res['size']/1024:.1f}KB"
                      if res["size"] < 1048576
                      else f"{res['size']/1048576:.2f}MB")
            manifest.setdefault(cat, []).append({
                "file": name, "url": url, "size": size_s
            })
            success += 1
        else:
            failed += 1

        time.sleep(delay)

    print()  # newline after progress
    section_end()
    ok(f"Assets done — {success} saved, {failed} failed")
    return success, failed

# ════════════════════════════════════════════════════════════════════
#  DEEP CRAWL
# ════════════════════════════════════════════════════════════════════
def crawl(start_url, max_pages=50, delay=0.35,
          do_assets=True, do_fonts=True, do_docs=False):

    base_host = urllib.parse.urlparse(start_url).netloc
    folder    = make_output_dir(start_url)
    visited   = set()
    queue     = deque([start_url])

    manifest = {
        "target":  start_url,
        "ip":      resolve_ip(start_url),
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages":   [],
        "css":     [], "js": [],
        "images":  [], "svg": [], "fonts": [],
        "docs":    [], "media": [], "assets": [],
    }

    # global asset sets — (url, category)
    all_assets: set = set()

    css_done  = set()
    js_done   = set()
    page_n    = 0

    section("DEEP CRAWL STARTED")
    info(f"Target  : {start_url}")
    info(f"IP      : {manifest['ip']}")
    info(f"Folder  : {folder}/")
    info(f"Max     : {max_pages} pages")
    info(f"Assets  : {'ON' if do_assets else 'OFF'}")
    section_end()

    while queue and page_n < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        p = urllib.parse.urlparse(url)
        if p.netloc != base_host:
            continue
        if not is_html_url(url) and page_n > 0:
            # treat as asset
            cat = asset_category(url)
            if cat and do_assets:
                all_assets.add((url, cat))
            continue

        visited.add(url)
        page_n += 1
        ptype  = page_type(url)

        print(f"  {G3}[{page_n:>3}]{RS}  {G1}{ptype:<10}{RS}  {DW}{url[:60]}{RS}")
        spin_start(f"Fetching page {page_n}...")
        res = raw_fetch(url)
        spin_stop()

        if not res["ok"]:
            err(f"Failed ({res['status']}) — {res.get('error','?')}")
            continue

        html = res["text"]

        # parse
        parser = LinkParser(url)
        try: parser.feed(html)
        except Exception: pass

        css_blocks, js_blocks = extract_inline(html)

        # filename
        fn = url_to_filename(url, page_n)
        if fn == "index.html" and page_n > 1:
            slug = re.sub(r'[^a-zA-Z0-9]','_', p.path.strip("/"))[:28]
            fn   = f"page_{page_n:03d}_{slug or 'page'}.html"

        write_text(folder, "pages", fn, html)

        # inline CSS
        for idx, blk in enumerate(css_blocks):
            if blk.strip():
                cname = f"{fn}_inline_{idx+1}.css"
                write_text(folder, "css", cname, blk)
                # extract url() from inline css
                for cu in extract_css_urls(blk, url):
                    cat = asset_category(cu)
                    if cat and do_assets:
                        all_assets.add((cu, cat))
                manifest["css"].append({"file": cname, "type": "inline", "from": url})

        # inline JS
        for idx, blk in enumerate(js_blocks):
            if blk.strip():
                jname = f"{fn}_inline_{idx+1}.js"
                write_text(folder, "js", jname, blk)
                manifest["js"].append({"file": jname, "type": "inline", "from": url})

        # external CSS
        for css_url in parser.css_links:
            if css_url in css_done: continue
            css_done.add(css_url)
            spin_start(f"CSS: {css_url[:45]}...")
            cr = raw_fetch(css_url)
            spin_stop()
            if cr["ok"]:
                cname = asset_safe_name(css_url)
                if not cname.endswith(".css"): cname += ".css"
                write_text(folder, "css", cname, cr["text"])
                # parse url() inside CSS
                for cu in extract_css_urls(cr["text"], css_url):
                    cat = asset_category(cu)
                    if cat and do_assets:
                        all_assets.add((cu, cat))
                manifest["css"].append({"file": cname, "url": css_url, "type": "external"})
                step(f"CSS  → css/{cname}")

        # external JS (same-domain only)
        for js_url in parser.js_links:
            if js_url in js_done: continue
            js_done.add(js_url)
            jp = urllib.parse.urlparse(js_url)
            if jp.netloc not in (base_host, ""): continue
            spin_start(f"JS: {js_url[:45]}...")
            jr = raw_fetch(js_url)
            spin_stop()
            if jr["ok"]:
                jname = asset_safe_name(js_url)
                if not jname.endswith(".js"): jname += ".js"
                write_text(folder, "js", jname, jr["text"])
                manifest["js"].append({"file": jname, "url": js_url, "type": "external"})
                step(f"JS   → js/{jname}")

        # collect image / svg / font urls
        if do_assets:
            for img_url in parser.img_links | parser.srcset_links | parser.bg_links:
                cat = asset_category(img_url)
                if not cat: cat = "images"
                if cat in ("images","svg","assets"):
                    all_assets.add((img_url, cat))

            for svg_url in parser.svg_links:
                all_assets.add((svg_url, "svg"))

            if do_fonts:
                for link in parser.css_links:
                    pass  # fonts extracted from CSS url() above

        # page record
        manifest["pages"].append({
            "url":     url,
            "file":    fn,
            "type":    ptype,
            "status":  res["status"],
            "size_kb": round(len(html.encode())/1024, 2),
            "lines":   html.count("\n")+1,
            "forms":   parser.forms,
            "server":  res.get("server","?"),
            "ct":      res.get("ct","?"),
        })
        saved(f"Page → pages/{fn}  ({res['status']})")

        # queue more links
        for link in parser.links:
            lp  = urllib.parse.urlparse(link)
            ext = os.path.splitext(lp.path)[1].lower()
            if lp.netloc == base_host and link not in visited:
                if ext in SKIP_EXTS: continue
                if ext in (IMAGE_EXTS | SVG_EXTS | FONT_EXTS
                           | DOC_EXTS | MEDIA_EXTS):
                    if do_assets:
                        cat = asset_category(link)
                        if cat: all_assets.add((link, cat))
                    continue
                queue.append(link)

        time.sleep(delay)

    # ── ASSET DOWNLOAD PHASE ──────────────────────────────────────
    if do_assets and all_assets:
        download_assets(folder, all_assets, manifest, delay=0.15)
    elif do_assets:
        info("No binary assets found.")

    return folder, manifest

# ════════════════════════════════════════════════════════════════════
#  SAVE MANIFEST
# ════════════════════════════════════════════════════════════════════
def save_manifest(folder, manifest):
    manifest["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    p = os.path.join(folder, "manifest.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

# ════════════════════════════════════════════════════════════════════
#  SUMMARY
# ════════════════════════════════════════════════════════════════════
def print_summary(folder, manifest):
    pages  = manifest["pages"]
    total  = len(pages)
    css_c  = len(manifest["css"])
    js_c   = len(manifest["js"])
    img_c  = len(manifest.get("images", []))
    svg_c  = len(manifest.get("svg", []))
    fnt_c  = len(manifest.get("fonts", []))
    doc_c  = len(manifest.get("docs", []))
    med_c  = len(manifest.get("media", []))
    kb     = sum(p.get("size_kb",0) for p in pages)
    forms  = sum(len(p.get("forms",[])) for p in pages)

    section("EXTRACTION COMPLETE")
    print(f"""
{G2}  ╔══════════════════════════════════════════════════════╗{RS}
{G2}  ║  {W}Target   {G1}: {manifest['target'][:46]:<46}{G2}║{RS}
{G2}  ║  {W}IP       {G1}: {manifest['ip']:<46}{G2}║{RS}
{G2}  ║  {W}Output   {G1}: {folder:<46}{G2}║{RS}
{G2}  ╠══════════════════════════════════════════════════════╣{RS}
{G2}  ║  {W}HTML Pages {G1}: {str(total):<44}{G2}║{RS}
{G2}  ║  {W}CSS Files  {G1}: {str(css_c):<44}{G2}║{RS}
{G2}  ║  {W}JS Files   {G1}: {str(js_c):<44}{G2}║{RS}
{G2}  ║  {W}Images     {G1}: {str(img_c):<44}{G2}║{RS}
{G2}  ║  {W}SVG Files  {G1}: {str(svg_c):<44}{G2}║{RS}
{G2}  ║  {W}Fonts      {G1}: {str(fnt_c):<44}{G2}║{RS}
{G2}  ║  {W}Documents  {G1}: {str(doc_c):<44}{G2}║{RS}
{G2}  ║  {W}Media      {G1}: {str(med_c):<44}{G2}║{RS}
{G2}  ║  {W}Forms      {G1}: {str(forms):<44}{G2}║{RS}
{G2}  ║  {W}HTML KB    {G1}: {f'{kb:.2f} KB':<44}{G2}║{RS}
{G2}  ╚══════════════════════════════════════════════════════╝{RS}
""")
    # folder tree
    print(f"{G3}  ── Folder Structure {'─'*36}{RS}")
    print(f"  {G1}{folder}/{RS}")
    for sub in ("pages","css","js","images","svg","fonts","docs","media"):
        p   = os.path.join(folder, sub)
        cnt = len(os.listdir(p)) if os.path.exists(p) else 0
        if cnt:
            bar = G2 + "├──" + RS
            print(f"  {bar} {G2}{sub:<10}{RS}  {DW}{cnt} files{RS}")

    # page index
    print(f"\n{G3}  ── Page Index {'─'*41}{RS}")
    for pg in pages:
        fm = f"  [{len(pg.get('forms',[]))} form]" if pg.get("forms") else ""
        print(f"  {G1}{pg['type']:<10}{RS}  {DW}{pg['file']:<38}{RS}  "
              f"{G2}{pg['status']}{RS}{YEL}{fm}{RS}")
    print()

# ════════════════════════════════════════════════════════════════════
#  FORM DETAILS
# ════════════════════════════════════════════════════════════════════
def print_forms(manifest):
    found = False
    for p in manifest["pages"]:
        forms = p.get("forms", [])
        if not forms: continue
        found = True
        print(f"\n{G1}  ◉ {p['url']}{RS}")
        for i, f in enumerate(forms, 1):
            print(f"  {G2}  Form {i}  action={W}{f['action'] or '/'}{RS}  "
                  f"method={W}{f['method']}{RS}")
            for inp in f["inputs"]:
                print(f"    {G3}  ├─ {DW}name={inp['name']:<22} "
                      f"type={inp['type']:<12} id={inp['id']}{RS}")
    if not found:
        info("No forms detected.")

# ════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ════════════════════════════════════════════════════════════════════
def main():
    banner()

    while True:
        # ── input URL ────────────────────────────────────────────
        print(f"{G2}  ╔══════════════════════════════════════════════════╗{RS}")
        print(f"{G2}  ║  {W}Target Website{G1} (exit = quit)                  {G2}║{RS}")
        print(f"{G2}  ╚══════════════════════════════════════════════════╝{RS}")
        print(f"{G1}  ❯❯ {RS}", end="")

        try:
            raw = input().strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{G3}  Crow leaving. Caw.{RS}\n")
            sys.exit(0)

        if raw.lower() in ("exit","quit","q"):
            print(f"\n{G3}  Crow leaving. Caw.{RS}\n")
            sys.exit(0)
        if not raw:
            warn("Enter a valid URL.")
            continue
        if not raw.startswith(("http://","https://")):
            raw = "https://" + raw

        # ── max pages ────────────────────────────────────────────
        print(f"{G2}  Max pages {DIM}[1-100, default 30]{RS}: ", end="")
        try:
            mp = input().strip()
            max_p = int(mp) if mp.isdigit() else 30
            max_p = min(max(max_p, 1), 100)
        except (KeyboardInterrupt, EOFError):
            max_p = 30

        # ── asset options ─────────────────────────────────────────
        print(f"""
{G2}  ╔══ Asset Download Options ══════════════════════════╗{RS}
{G2}  ║  {G1}[1]{W} Images + SVG + Fonts  (recommended)      {G2}║{RS}
{G2}  ║  {G1}[2]{W} Images + SVG only                        {G2}║{RS}
{G2}  ║  {G1}[3]{W} All assets (+ docs + media)              {G2}║{RS}
{G2}  ║  {G1}[4]{W} Source only (no asset download)          {G2}║{RS}
{G2}  ╚════════════════════════════════════════════════════╝{RS}""")
        print(f"{G1}  Choice {DIM}[default: 1]{RS}: ", end="")
        try:
            ch = input().strip()
        except (KeyboardInterrupt, EOFError):
            ch = "1"

        do_assets = ch != "4"
        do_fonts  = ch in ("1","3","")
        do_docs   = ch == "3"

        print(f"\n{G1}  ⚡ Target locked: {W}{raw}{RS}\n")

        try:
            folder, manifest = crawl(
                raw, max_pages=max_p, delay=0.3,
                do_assets=do_assets,
                do_fonts=do_fonts,
                do_docs=do_docs,
            )
            save_manifest(folder, manifest)
            print_summary(folder, manifest)

            print(f"{G2}  Show form details? {G1}[y/N]{RS}: ", end="")
            try:
                ans = input().strip().lower()
            except (KeyboardInterrupt, EOFError):
                ans = "n"
            if ans == "y":
                print_forms(manifest)

        except KeyboardInterrupt:
            spin_stop()
            print(f"\n\n{YEL}  Scan interrupted.{RS}\n")

        print(f"\n{G1}  Delivered. {G2}Another target?{RS}\n")

# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
