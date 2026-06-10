#!/usr/bin/env python3
"""
Dubai Sale — Sheets → HTML Builder
"""

import csv
import urllib.request
import urllib.parse
import os
from datetime import datetime

SHEET_CSV_URL   = os.environ.get("SHEET_CSV_URL", "")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "971XXXXXXXXX")
EMAIL           = os.environ.get("CONTACT_EMAIL", "YOUR@EMAIL.COM")
SITE_TITLE      = os.environ.get("SITE_TITLE", "Dubai Home Sale – Quality Furniture & More")

CATEGORIES = {
    "living":  ("Living Room",      "🛋️"),
    "bedroom": ("Bedroom",          "🛏️"),
    "kitchen": ("Kitchen & Dining", "🍽️"),
    "decor":   ("Decor & Lighting", "💡"),
    "outdoor": ("Outdoor",          "🌿"),
    "other":   ("Other",            "📦"),
}

STATUS_BADGE = {
    "available": ("badge-available", "Available"),
    "sold":      ("badge-sold",      "Sold"),
    "reserved":  ("badge-reserved",  "Reserved"),
}

def fetch_items():
    if not SHEET_CSV_URL:
        print("⚠️ No SHEET_CSV_URL — using sample data")
        return get_sample_items()
    req = urllib.request.Request(SHEET_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")
    reader = csv.DictReader(content.splitlines())
    items = []
    for row in reader:
        status = row.get("status", "available").strip().lower()
        # N/A veya boş status → siteye ekleme
        if status in ("n/a", "na", ""):
            continue
        photos = []
        if row.get("photo_1", "").strip():
            for col in ("photo_1", "photo_2", "photo_3"):
                v = row.get(col, "").strip()
                if v:
                    photos.append(v)
        else:
            photos_raw = row.get("photo", "").strip()
            photos = [p.strip() for p in photos_raw.split(";") if p.strip()]
        items.append({
            "name":        row.get("name", "").strip(),
            "description": row.get("description", "").strip(),
            "price":       row.get("price", "").strip(),
            "category":    row.get("category", "other").strip().lower(),
            "status":      status,
            "emoji":       row.get("emoji", "📦").strip(),
            "photos":      photos,
        })
    return [i for i in items if i["name"]]

def get_sample_items():
    return [
        {"name":"L-Shaped Sectional Sofa","description":"Light grey modular sofa","price":"2000","category":"living","status":"available","emoji":"🛋️","photos":[]},
        {"name":"Glass Coffee Table","description":"Metal frame glass top","price":"600","category":"living","status":"available","emoji":"☕","photos":[]},
    ]

def render_slider(photos, name, emoji, item_id):
    if not photos:
        return f'<div class="img-placeholder" onclick="openLightbox({item_id}, 0)">{emoji}</div>'
    if len(photos) == 1:
        return f'''<div class="item-img" onclick="openLightbox({item_id}, 0)">
<img src="photos/{photos[0]}" alt="{name}" loading="lazy">
<div class="zoom-hint">🔍</div>
</div>'''
    uid = f"s{item_id}"
    slides = ""
    dots = ""
    for i, photo in enumerate(photos):
        active = " active" if i == 0 else ""
        slides += f'<img class="slide{active}" src="photos/{photo}" alt="{name} {i+1}" loading="lazy" onclick="openLightbox({item_id},{i})">\n'
        dots += f'<span class="dot{active}" onclick="goSlide(\'{uid}\',{i})"></span>\n'
    return f'''<div class="slider" id="slider-{uid}">
{slides}
<button class="sl-btn sl-prev" onclick="changeSlide(\'{uid}\',-1)">&#8249;</button>
<button class="sl-btn sl-next" onclick="changeSlide(\'{uid}\',1)">&#8250;</button>
<div class="dots">{dots}</div>
<span class="photo-count">🔍 {len(photos)} photos</span>
</div>'''

def render_item_card(item, item_id):
    status = item["status"]
    badge_cls, badge_label = STATUS_BADGE.get(status, ("badge-available", "Available"))
    is_sold = status in ("sold", "reserved")
    card_cls = "item-card sold" if is_sold else "item-card"
    img_html = render_slider(item["photos"], item["name"], item["emoji"], item_id)
    price_raw = item["price"].replace(",", "")
    price_display = f"{int(price_raw):,}" if price_raw.isdigit() else item["price"]

    if is_sold:
        action_btn = f'<button class="inquire-btn disabled">{badge_label}</button>'
    else:
        action_btn = f'<button class="add-to-cart-btn" onclick="addToCart({item_id})">+ Add to List</button>'

    return f'''  <div class="{card_cls}" data-category="{item['category']}" id="card-{item_id}">
    {img_html}
    <span class="status-badge {badge_cls}">{badge_label}</span>
    <div class="item-body">
      <div class="item-name">{item['name']}</div>
      <div class="item-desc">{item['description']}</div>
      <div class="item-footer">
        <div class="item-price">{price_display} <span>AED</span></div>
        {action_btn}
      </div>
    </div>
  </div>'''

def render_html(items, email, title):
    for idx, item in enumerate(items):
        item["_id"] = idx

    by_cat = {k: [] for k in CATEGORIES}
    for item in items:
        cat = item["category"] if item["category"] in CATEGORIES else "other"
        by_cat[cat].append(item)

    sections_html = ""
    for cat_key, (cat_label, _) in CATEGORIES.items():
        cat_items = by_cat[cat_key]
        if not cat_items:
            continue
        available = sum(1 for i in cat_items if i["status"] == "available")
        cards = "\n".join(render_item_card(i, i["_id"]) for i in cat_items)
        sections_html += f'''
<section class="category-section" data-category="{cat_key}">
  <h2 class="category-title">{cat_label}</h2>
  <p class="category-count">{available} available of {len(cat_items)}</p>
  <div class="items-grid">
{cards}
  </div>
</section>'''

    items_json = "[\n"
    for item in items:
        photos_js = str(item["photos"]).replace("'", '"')
        items_json += f'  {{"id":{item["_id"]},"name":{repr(item["name"])},"price":"{item["price"]}","photos":{photos_js},"emoji":"{item["emoji"]}","status":"{item["status"]}"}},\n'
    items_json += "]"

    updated       = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    total         = len(items)
    available_total = sum(1 for i in items if i["status"] == "available")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --cream:#f5f0e8; --warm-white:#faf7f2; --sand:#e8dcc8;
  --taupe:#c4a882; --brown:#8b6f47; --dark-brown:#4a3728;
  --text:#2c1f14; --text-light:#7a6552;
  --sold:#c0392b; --available:#6b8c6b;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--warm-white);color:var(--text);font-family:'Jost',sans-serif;font-weight:300}}
header{{background:var(--dark-brown);color:var(--cream);padding:60px 40px 50px;text-align:center;position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 50%,rgba(196,168,130,.15) 0%,transparent 60%)}}
header *{{position:relative}}
.header-tag{{font-size:11px;letter-spacing:4px;text-transform:uppercase;color:var(--taupe);margin-bottom:16px}}
h1{{font-family:'Cormorant Garamond',serif;font-size:clamp(38px,6vw,64px);font-weight:300;line-height:1.1;margin-bottom:12px}}
h1 em{{font-style:italic;color:var(--taupe)}}
.header-sub{{font-size:14px;color:rgba(245,240,232,.65);letter-spacing:1px;margin-bottom:8px}}
.header-stats{{font-size:13px;color:var(--taupe);margin-bottom:28px;letter-spacing:1px}}
.contact-bar{{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}}
.contact-btn{{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;border-radius:2px;font-size:13px;letter-spacing:2px;text-transform:uppercase;text-decoration:none;transition:all .25s;cursor:pointer;font-family:'Jost',sans-serif;border:none}}
.btn-email{{background:transparent;color:var(--cream);border:1px solid rgba(245,240,232,.3)}}
.btn-email:hover{{border-color:var(--taupe);color:var(--taupe);transform:translateY(-2px)}}
.notice{{background:var(--sand);text-align:center;padding:14px 20px;font-size:13px;color:var(--dark-brown)}}
main{{max-width:1200px;margin:0 auto;padding:20px 24px 80px}}
.top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;padding:32px 0 24px;border-bottom:1px solid var(--sand);margin-bottom:40px}}
.filter-nav{{display:flex;gap:8px;flex-wrap:wrap}}
.filter-btn{{padding:8px 20px;border:1px solid var(--sand);background:transparent;color:var(--text-light);font-family:'Jost',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;border-radius:2px;transition:all .2s}}
.filter-btn:hover,.filter-btn.active{{background:var(--dark-brown);border-color:var(--dark-brown);color:var(--cream)}}
.top-actions{{display:flex;gap:10px}}
.cart-btn{{display:flex;align-items:center;gap:8px;padding:10px 20px;background:var(--brown);color:white;border:none;border-radius:2px;font-family:'Jost',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;transition:all .2s}}
.cart-btn:hover{{background:var(--dark-brown)}}
.cart-count{{background:white;color:var(--brown);border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:500}}
.pdf-btn{{display:flex;align-items:center;gap:8px;padding:10px 20px;background:transparent;color:var(--dark-brown);border:1px solid var(--sand);border-radius:2px;font-family:'Jost',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;transition:all .2s}}
.pdf-btn:hover{{background:var(--sand)}}
.category-section{{margin-bottom:56px}}
.category-title{{font-family:'Cormorant Garamond',serif;font-size:28px;font-weight:300;color:var(--dark-brown);margin-bottom:6px;display:flex;align-items:center;gap:16px}}
.category-title::after{{content:'';flex:1;height:1px;background:var(--sand)}}
.category-count{{font-size:12px;color:var(--text-light);letter-spacing:1px;margin-bottom:24px}}
.items-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:24px}}
.item-card{{background:white;border:1px solid var(--sand);border-radius:4px;overflow:hidden;transition:transform .25s,box-shadow .25s;position:relative}}
.item-card:hover{{transform:translateY(-4px);box-shadow:0 12px 32px rgba(74,55,40,.12)}}
.item-card.sold{{opacity:.6}}
.item-card.in-cart{{border:2px solid var(--brown)}}
.item-img{{width:100%;aspect-ratio:4/3;overflow:hidden;cursor:zoom-in;position:relative}}
.item-img img{{width:100%;height:100%;object-fit:cover;transition:transform .3s}}
.item-img:hover img{{transform:scale(1.03)}}
.zoom-hint{{position:absolute;bottom:8px;right:8px;background:rgba(74,55,40,.6);color:white;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:13px;opacity:0;transition:opacity .2s}}
.item-img:hover .zoom-hint{{opacity:1}}
.img-placeholder{{width:100%;aspect-ratio:4/3;background:linear-gradient(135deg,var(--cream) 0%,var(--sand) 100%);display:flex;align-items:center;justify-content:center;color:var(--taupe);font-size:36px;cursor:pointer}}
.slider{{position:relative;width:100%;aspect-ratio:4/3;overflow:hidden;background:var(--sand)}}
.slider .slide{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .35s ease;cursor:zoom-in}}
.slider .slide.active{{opacity:1}}
.sl-btn{{position:absolute;top:50%;transform:translateY(-50%);background:rgba(74,55,40,.55);color:white;border:none;width:32px;height:32px;font-size:20px;cursor:pointer;border-radius:2px;z-index:2;transition:background .2s;display:flex;align-items:center;justify-content:center}}
.sl-btn:hover{{background:rgba(74,55,40,.85)}}
.sl-prev{{left:8px}}.sl-next{{right:8px}}
.dots{{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);display:flex;gap:5px;z-index:2}}
.dot{{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,.5);cursor:pointer;transition:background .2s}}
.dot.active{{background:white}}
.photo-count{{position:absolute;bottom:8px;right:10px;font-size:10px;color:rgba(255,255,255,.8);z-index:2;cursor:zoom-in}}
.status-badge{{position:absolute;top:12px;right:12px;padding:4px 10px;font-size:10px;letter-spacing:2px;text-transform:uppercase;font-weight:500;border-radius:2px;z-index:3}}
.badge-available{{background:var(--available);color:white}}
.badge-sold{{background:var(--sold);color:white}}
.badge-reserved{{background:#d4a017;color:white}}
.in-cart-badge{{position:absolute;top:12px;left:12px;background:var(--brown);color:white;padding:4px 10px;font-size:10px;letter-spacing:2px;text-transform:uppercase;border-radius:2px;z-index:3;display:none}}
.item-card.in-cart .in-cart-badge{{display:block}}
.item-body{{padding:16px 18px 18px}}
.item-name{{font-family:'Cormorant Garamond',serif;font-size:20px;font-weight:400;margin-bottom:4px;color:var(--dark-brown)}}
.item-desc{{font-size:13px;color:var(--text-light);line-height:1.5;margin-bottom:12px}}
.item-footer{{display:flex;align-items:center;justify-content:space-between}}
.item-price{{font-family:'Cormorant Garamond',serif;font-size:22px;font-weight:600;color:var(--brown)}}
.item-price span{{font-size:13px;font-weight:300;color:var(--text-light)}}
.inquire-btn,.add-to-cart-btn{{padding:7px 16px;border-radius:2px;font-family:'Jost',sans-serif;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;text-decoration:none;display:inline-block;transition:all .2s;border:none}}
.inquire-btn{{background:var(--dark-brown);color:var(--cream)}}
.inquire-btn.disabled{{background:#ccc;cursor:not-allowed;pointer-events:none}}
.add-to-cart-btn{{background:var(--dark-brown);color:var(--cream)}}
.add-to-cart-btn:hover{{background:var(--brown)}}
.item-card.in-cart .add-to-cart-btn{{background:var(--sold)}}
.item-card.in-cart .add-to-cart-btn::after{{content:' ✓'}}
/* Lightbox */
.lightbox{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:1000;align-items:center;justify-content:center}}
.lightbox.open{{display:flex}}
.lb-inner{{position:relative;max-width:90vw;max-height:90vh}}
.lb-inner img{{max-width:90vw;max-height:85vh;object-fit:contain;border-radius:2px}}
.lb-close{{position:fixed;top:20px;right:28px;color:white;font-size:36px;cursor:pointer;background:none;border:none;line-height:1;opacity:.8}}
.lb-close:hover{{opacity:1}}
.lb-prev,.lb-next{{position:fixed;top:50%;transform:translateY(-50%);background:rgba(255,255,255,.15);color:white;border:none;font-size:32px;padding:12px 18px;cursor:pointer;border-radius:2px;transition:background .2s}}
.lb-prev:hover,.lb-next:hover{{background:rgba(255,255,255,.3)}}
.lb-prev{{left:16px}}.lb-next{{right:16px}}
.lb-counter{{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.6);font-size:13px;letter-spacing:2px}}
/* Cart Drawer */
.cart-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:500}}
.cart-overlay.open{{display:block}}
.cart-drawer{{position:fixed;right:0;top:0;bottom:0;width:380px;max-width:95vw;background:var(--warm-white);z-index:501;display:flex;flex-direction:column;transform:translateX(100%);transition:transform .3s ease;box-shadow:-4px 0 24px rgba(0,0,0,.15)}}
.cart-drawer.open{{transform:translateX(0)}}
.cart-header{{padding:24px;border-bottom:1px solid var(--sand);display:flex;justify-content:space-between;align-items:center}}
.cart-header h3{{font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:300;color:var(--dark-brown)}}
.cart-close{{background:none;border:none;font-size:24px;cursor:pointer;color:var(--text-light)}}
.cart-items{{flex:1;overflow-y:auto;padding:16px 24px}}
.cart-item{{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid var(--sand)}}
.cart-item-img{{width:60px;height:60px;object-fit:cover;border-radius:2px;background:var(--sand);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}}
.cart-item-img img{{width:60px;height:60px;object-fit:cover;border-radius:2px}}
.cart-item-info{{flex:1}}
.cart-item-name{{font-family:'Cormorant Garamond',serif;font-size:17px;color:var(--dark-brown);margin-bottom:2px}}
.cart-item-price{{font-size:13px;color:var(--brown);font-weight:500}}
.cart-item-remove{{background:none;border:none;color:var(--text-light);cursor:pointer;font-size:18px;padding:0 4px}}
.cart-item-remove:hover{{color:var(--sold)}}
.cart-empty{{text-align:center;padding:40px 20px;color:var(--text-light);font-size:14px}}
.cart-footer{{padding:20px 24px;border-top:1px solid var(--sand)}}
.cart-total{{display:flex;justify-content:space-between;margin-bottom:16px;font-family:'Cormorant Garamond',serif;font-size:20px;color:var(--dark-brown)}}
.cart-actions{{display:flex;flex-direction:column;gap:10px}}
.cart-email-btn{{padding:14px;border-radius:2px;font-family:'Jost',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;border:none;transition:all .2s;text-align:center;text-decoration:none;display:block;background:var(--dark-brown);color:var(--cream)}}
.cart-email-btn:hover{{background:var(--brown)}}
.cart-pdf-btn{{padding:14px;border-radius:2px;font-family:'Jost',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;border:1px solid var(--sand);background:transparent;color:var(--dark-brown);transition:all .2s;text-align:center;display:block;width:100%}}
.cart-pdf-btn:hover{{background:var(--sand)}}
footer{{background:var(--dark-brown);color:rgba(245,240,232,.6);text-align:center;padding:32px 20px;font-size:13px}}
footer strong{{color:var(--taupe)}}
.updated{{font-size:11px;opacity:.5;margin-top:10px}}
@media print{{
  header .contact-bar,.top-actions,.add-to-cart-btn,.inquire-btn,.sl-btn,.dots,footer{{display:none!important}}
  .item-card{{break-inside:avoid}}
  body{{background:white}}
}}
@media(max-width:600px){{
  header{{padding:40px 20px 36px}}
  .items-grid{{grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}}
  .item-name{{font-size:17px}}
  .cart-drawer{{width:100vw}}
}}
</style>
</head>
<body>
<header>
  <p class="header-tag">Dubai · Relocating Sale</p>
  <p class="header-sub">All items available for viewing in Dubai · Priced to sell fast</p>
  <p class="header-stats">{available_total} of {total} items still available</p>
  <div class="contact-bar">
    <a href="mailto:{email}?subject=Dubai Home Sale Inquiry" class="contact-btn btn-email">✉ Email</a>
  </div>
</header>
<div class="notice">
  <strong>Pick-up only</strong> · Dubai location shared upon inquiry 
</div>
<main>
  <div class="top-bar">
    <nav class="filter-nav">
      <button class="filter-btn active" onclick="filterCategory('all',this)">All Items</button>
      <button class="filter-btn" onclick="filterCategory('living',this)">Living Room</button>
      <button class="filter-btn" onclick="filterCategory('bedroom',this)">Bedroom</button>
      <button class="filter-btn" onclick="filterCategory('kitchen',this)">Kitchen &amp; Dining</button>
      <button class="filter-btn" onclick="filterCategory('decor',this)">Decor &amp; Lighting</button>
      <button class="filter-btn" onclick="filterCategory('outdoor',this)">Outdoor</button>
      <button class="filter-btn" onclick="filterCategory('other',this)">Other</button>
    </nav>
    <div class="top-actions">
      <button class="pdf-btn" onclick="window.print()">🖨 Save PDF</button>
      <button class="cart-btn" onclick="openCart()">🛒 My List <span class="cart-count" id="cartCount">0</span></button>
    </div>
  </div>
  {sections_html}
</main>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
  <button class="lb-close" onclick="closeLightbox()">×</button>
  <button class="lb-prev" onclick="lbNav(-1);event.stopPropagation()">&#8249;</button>
  <div class="lb-inner"><img id="lbImg" src="" alt=""></div>
  <button class="lb-next" onclick="lbNav(1);event.stopPropagation()">&#8250;</button>
  <div class="lb-counter" id="lbCounter"></div>
</div>

<!-- Cart Drawer -->
<div class="cart-overlay" id="cartOverlay" onclick="closeCart()"></div>
<div class="cart-drawer" id="cartDrawer">
  <div class="cart-header">
    <h3>My Interest List</h3>
    <button class="cart-close" onclick="closeCart()">×</button>
  </div>
  <div class="cart-items" id="cartItems"></div>
  <div class="cart-footer" id="cartFooter" style="display:none">
    <div class="cart-total"><span>Total</span><span id="cartTotal">0 AED</span></div>
    <div class="cart-actions">
      <a id="cartEmailBtn" href="#" class="cart-email-btn">✉ Send via Email</a>
      <button onclick="printList()" class="cart-pdf-btn">🖨 Save as PDF</button>
    </div>
  </div>
</div>

<footer>
  <p>📍 Dubai · <strong>Pick-up only</strong> · All items sold as-is</p>
  <p style="margin-top:8px">Questions? <strong>Email</strong> — responses within a few hours</p>
  <p class="updated">Last updated: {updated}</p>
</footer>

<script>
const ITEMS = {items_json};
const EMAIL_ADDR = "{email}";
let cart = [];

function filterCategory(cat,btn){{
  document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.category-section').forEach(sec=>{{
    sec.style.display=(cat==='all'||sec.dataset.category===cat)?'':'none';
  }});
}}

function changeSlide(uid,dir){{
  const sl=document.getElementById('slider-'+uid);
  const slides=[...sl.querySelectorAll('.slide')];
  const dots=[...sl.querySelectorAll('.dot')];
  let cur=slides.findIndex(s=>s.classList.contains('active'));
  slides[cur].classList.remove('active'); dots[cur].classList.remove('active');
  cur=(cur+dir+slides.length)%slides.length;
  slides[cur].classList.add('active'); dots[cur].classList.add('active');
}}
function goSlide(uid,idx){{
  const sl=document.getElementById('slider-'+uid);
  sl.querySelectorAll('.slide').forEach((s,i)=>s.classList.toggle('active',i===idx));
  sl.querySelectorAll('.dot').forEach((d,i)=>d.classList.toggle('active',i===idx));
}}

let lbItem=null, lbIdx=0;
function openLightbox(itemId,photoIdx){{
  lbItem=ITEMS[itemId]; lbIdx=photoIdx;
  if(!lbItem.photos||lbItem.photos.length===0) return;
  showLbPhoto();
  document.getElementById('lightbox').classList.add('open');
  document.body.style.overflow='hidden';
}}
function showLbPhoto(){{
  const photos=lbItem.photos;
  document.getElementById('lbImg').src='photos/'+photos[lbIdx];
  document.getElementById('lbCounter').textContent=photos.length>1?(lbIdx+1)+' / '+photos.length:'';
  document.querySelector('.lb-prev').style.display=photos.length>1?'':'none';
  document.querySelector('.lb-next').style.display=photos.length>1?'':'none';
}}
function lbNav(dir){{
  lbIdx=(lbIdx+dir+lbItem.photos.length)%lbItem.photos.length;
  showLbPhoto();
}}
function closeLightbox(e){{
  if(e&&e.target!==document.getElementById('lightbox')&&!e.target.classList.contains('lb-close')) return;
  document.getElementById('lightbox').classList.remove('open');
  document.body.style.overflow='';
}}
document.addEventListener('keydown',e=>{{
  if(!document.getElementById('lightbox').classList.contains('open')) return;
  if(e.key==='Escape') closeLightbox();
  if(e.key==='ArrowLeft') lbNav(-1);
  if(e.key==='ArrowRight') lbNav(1);
}});

function addToCart(itemId){{
  const item=ITEMS[itemId];
  const card=document.getElementById('card-'+itemId);
  if(cart.find(i=>i.id===itemId)){{
    cart=cart.filter(i=>i.id!==itemId);
    card.classList.remove('in-cart');
  }} else {{
    cart.push(item);
    card.classList.add('in-cart');
  }}
  updateCartCount();
}}
function updateCartCount(){{
  document.getElementById('cartCount').textContent=cart.length;
}}
function openCart(){{
  renderCart();
  document.getElementById('cartDrawer').classList.add('open');
  document.getElementById('cartOverlay').classList.add('open');
  document.body.style.overflow='hidden';
}}
function closeCart(){{
  document.getElementById('cartDrawer').classList.remove('open');
  document.getElementById('cartOverlay').classList.remove('open');
  document.body.style.overflow='';
}}
function renderCart(){{
  const el=document.getElementById('cartItems');
  const footer=document.getElementById('cartFooter');
  if(cart.length===0){{
    el.innerHTML='<div class="cart-empty">Your interest list is empty.<br><br>Click "+ Add to List" on items you are interested in.</div>';
    footer.style.display='none'; return;
  }}
  let total=0, html='';
  cart.forEach(item=>{{
    const price=parseInt(item.price.replace(/,/g,''))||0;
    total+=price;
    const imgHtml=item.photos&&item.photos.length>0
      ?`<img src="photos/${{item.photos[0]}}" alt="${{item.name}}">`
      :`<div style="width:60px;height:60px;background:var(--sand);display:flex;align-items:center;justify-content:center;font-size:24px;border-radius:2px">${{item.emoji}}</div>`;
    html+=`<div class="cart-item">
      <div class="cart-item-img">${{imgHtml}}</div>
      <div class="cart-item-info">
        <div class="cart-item-name">${{item.name}}</div>
        <div class="cart-item-price">${{item.price}} AED</div>
      </div>
      <button class="cart-item-remove" onclick="removeFromCart(${{item.id}})">×</button>
    </div>`;
  }});
  el.innerHTML=html;
  document.getElementById('cartTotal').textContent=total.toLocaleString()+' AED';
  footer.style.display='block';

  let emailBody='Hi,\\n\\nI am interested in the following items:\\n\\n';
  cart.forEach(item=>{{ emailBody+=`• ${{item.name}} – ${{item.price}} AED\\n`; }});
  emailBody+=`\\nTotal: ${{total.toLocaleString()}} AED`;
  document.getElementById('cartEmailBtn').href='mailto:'+EMAIL_ADDR+'?subject=Dubai Home Sale - Interest List&body='+encodeURIComponent(emailBody);
}}
function printList(){{
  if(cart.length===0) return;
  var total=0, rows='';
  cart.forEach(function(item){{
    var p=parseInt(item.price.replace(/,/g,''))||0; total+=p;
    rows+='<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;font-size:14px"><span>'+item.emoji+' '+item.name+'</span><span style="font-weight:600">'+item.price+' AED</span></div>';
  }});
  var w=window.open('','_blank');
  w.document.write(`<html><head><title>My Interest List</title>
  <style>body{{font-family:Georgia,serif;max-width:600px;margin:40px auto;padding:0 20px;color:#2c1f14}}
  h2{{color:#4a3728;margin-bottom:4px;font-size:24px}}
  .sub{{font-size:12px;color:#7a6552;margin-bottom:20px;letter-spacing:1px}}
  .tot{{font-weight:700;text-align:right;margin-top:16px;font-size:16px;color:#4a3728}}
  .ft{{margin-top:24px;font-size:11px;color:#aaa;border-top:1px solid #eee;padding-top:12px}}</style>
  </head><body>
  <h2>My Interest List</h2>
  <div class="sub">DUBAI HOME SALE</div>
  ${{rows}}
  <div class="tot">Total: ${{total.toLocaleString()}} AED</div>
  <div class="ft">Dubai · Pick-up only · All items sold as-is</div>
  <script>window.onload=function(){{window.print();}}</scr'+'ipt>
  </body></html>`);
  w.document.close();
}}
function removeFromCart(itemId){{
  cart=cart.filter(i=>i.id!==itemId);
  document.getElementById('card-'+itemId)?.classList.remove('in-cart');
  updateCartCount();
  renderCart();
}}
</script>
</body>
</html>'''

if __name__ == "__main__":
    print("🔨 Building Dubai Sale site...")
    items = fetch_items()
    print(f"   Found {len(items)} items")
    html = render_html(items, EMAIL, SITE_TITLE)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html generated successfully")
