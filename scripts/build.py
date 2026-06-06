#!/usr/bin/env python3
"""
Dubai Sale — Sheets → HTML Builder
Reads public Google Sheet (CSV export) and generates index.html
"""

import csv
import urllib.request
import os
import json
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────
# Paste your Google Sheet's CSV export URL here after setup:
SHEET_CSV_URL = os.environ.get("SHEET_CSV_URL", "")

WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "971XXXXXXXXX")
EMAIL = os.environ.get("CONTACT_EMAIL", "YOUR@EMAIL.COM")
SITE_TITLE = os.environ.get("SITE_TITLE", "Dubai Home Sale – Quality Furniture & More")
# ───────────────────────────────────────────────────────────────────────────

CATEGORIES = {
    "living":   ("Living Room",    "🛋️"),
    "bedroom":  ("Bedroom",        "🛏️"),
    "kitchen":  ("Kitchen & Dining","🍽️"),
    "decor":    ("Decor & Lighting","💡"),
    "outdoor":  ("Outdoor",        "🌿"),
    "other":    ("Other",          "📦"),
}

STATUS_BADGE = {
    "available": ("badge-available", "Available"),
    "sold":      ("badge-sold",      "Sold"),
    "reserved":  ("badge-reserved",  "Reserved"),
}

def fetch_items():
    """Fetch items from Google Sheets CSV export."""
    if not SHEET_CSV_URL:
        print("⚠️  No SHEET_CSV_URL set — using sample data")
        return get_sample_items()
    
    req = urllib.request.Request(SHEET_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")
    
    reader = csv.DictReader(content.splitlines())
    items = []
    for row in reader:
        # Expected columns: name, description, price, category, status, emoji, photo
        items.append({
            "name":        row.get("name", "").strip(),
            "description": row.get("description", "").strip(),
            "price":       row.get("price", "").strip(),
            "category":    row.get("category", "other").strip().lower(),
            "status":      row.get("status", "available").strip().lower(),
            "emoji":       row.get("emoji", "📦").strip(),
            "photo":       row.get("photo", "").strip(),
        })
    return [i for i in items if i["name"]]  # skip empty rows

def get_sample_items():
    """Fallback sample data for first build."""
    return [
        {"name":"3-Seater Sofa","description":"Grey fabric, excellent condition. IKEA. 2 years old.","price":"1200","category":"living","status":"available","emoji":"🛋️","photo":""},
        {"name":"Round Wall Mirror","description":"80cm diameter. Dark wood frame.","price":"350","category":"living","status":"available","emoji":"🪞","photo":""},
        {"name":"Armchair","description":"Beige boucle, very comfortable, minimal use.","price":"600","category":"living","status":"available","emoji":"🪑","photo":""},
        {"name":"Coffee Table","description":"Walnut finish. 120x60cm.","price":"800","category":"living","status":"sold","emoji":"🪴","photo":""},
        {"name":"King Bed Frame","description":"Upholstered, light grey. 180x200cm. No mattress.","price":"1500","category":"bedroom","status":"available","emoji":"🛏️","photo":""},
        {"name":"Wardrobe","description":"6-door white IKEA PAX with mirror.","price":"900","category":"bedroom","status":"reserved","emoji":"🗄️","photo":""},
        {"name":"Bedside Tables ×2","description":"Matching pair, white with drawers.","price":"300","category":"bedroom","status":"available","emoji":"🪞","photo":""},
        {"name":"Dining Table","description":"Solid wood, seats 6. 160x90cm.","price":"1100","category":"kitchen","status":"available","emoji":"🍽️","photo":""},
        {"name":"Dining Chairs ×4","description":"Upholstered, camel colour.","price":"480","category":"kitchen","status":"available","emoji":"🪑","photo":""},
        {"name":"Nespresso Machine","description":"Vertuo Next. Includes capsule holder. Works perfectly.","price":"220","category":"kitchen","status":"available","emoji":"☕","photo":""},
        {"name":"Floor Lamp","description":"White ceramic base, linen shade. 165cm.","price":"280","category":"decor","status":"available","emoji":"💡","photo":""},
        {"name":"Large Plant Pot","description":"Terracotta, 45cm diameter. Plant not included.","price":"80","category":"decor","status":"available","emoji":"🪴","photo":""},
        {"name":"Wall Art Set ×3","description":"3 framed prints, neutral tones. 40x50cm each.","price":"150","category":"decor","status":"available","emoji":"🖼️","photo":""},
        {"name":"Balcony Table & Chairs","description":"Rattan 2-seater with table. Used one season.","price":"450","category":"outdoor","status":"available","emoji":"🌿","photo":""},
        {"name":"Sun Umbrella","description":"3m diameter. Cream with base.","price":"200","category":"outdoor","status":"available","emoji":"☂️","photo":""},
        {"name":"Office Desk","description":"White, 140x70cm. Manual height adjustment.","price":"700","category":"other","status":"available","emoji":"🖥️","photo":""},
        {"name":"Storage Shelves","description":"Metal 5-tier unit. 180x90x40cm. Black.","price":"250","category":"other","status":"available","emoji":"📦","photo":""},
    ]

def render_item_card(item, wa_number):
    status = item["status"]
    badge_cls, badge_label = STATUS_BADGE.get(status, ("badge-available", "Available"))
    is_sold = status in ("sold", "reserved")
    card_cls = "item-card sold" if is_sold else "item-card"
    
    # Image or placeholder
    if item["photo"]:
        img_html = f'''<div class="item-img">
          <img src="photos/{item['photo']}" alt="{item['name']}" loading="lazy">
        </div>'''
    else:
        img_html = f'<div class="img-placeholder">{item["emoji"]}</div>'
    
    # Button
    item_name_encoded = urllib.parse.quote(item["name"])
    if is_sold:
        btn = f'<button class="inquire-btn disabled">{badge_label}</button>'
    else:
        wa_msg = f"Hi, I'm interested in the {item['name']}"
        wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_msg)}"
        btn = f'<a href="{wa_url}" class="inquire-btn">Inquire</a>'
    
    price_display = f"{int(item['price']):,}" if item["price"].isdigit() else item["price"]
    
    return f'''      <div class="{card_cls}" data-category="{item['category']}">
        {img_html}
        <span class="status-badge {badge_cls}">{badge_label}</span>
        <div class="item-body">
          <div class="item-name">{item['name']}</div>
          <div class="item-desc">{item['description']}</div>
          <div class="item-footer">
            <div class="item-price">{price_display} <span>AED</span></div>
            {btn}
          </div>
        </div>
      </div>'''

def render_html(items, wa_number, email, title):
    import urllib.parse  # ensure available in scope
    
    # Group by category
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
        count_label = f"{available} available of {len(cat_items)}"
        cards = "\n".join(render_item_card(i, wa_number) for i in cat_items)
        sections_html += f'''
  <section class="category-section" data-category="{cat_key}">
    <h2 class="category-title">{cat_label}</h2>
    <p class="category-count">{count_label}</p>
    <div class="items-grid">
{cards}
    </div>
  </section>'''

    wa_url_general = f"https://wa.me/{wa_number}?text={urllib.parse.quote('Hi, I am interested in an item from your sale')}"
    updated = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    
    total = len(items)
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
    --cream: #f5f0e8;
    --warm-white: #faf7f2;
    --sand: #e8dcc8;
    --taupe: #c4a882;
    --brown: #8b6f47;
    --dark-brown: #4a3728;
    --text: #2c1f14;
    --text-light: #7a6552;
    --sold: #c0392b;
    --available: #6b8c6b;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--warm-white); color: var(--text); font-family: 'Jost', sans-serif; font-weight: 300; }}
  header {{ background: var(--dark-brown); color: var(--cream); padding: 60px 40px 50px; text-align: center; position: relative; overflow: hidden; }}
  header::before {{ content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse at 30% 50%, rgba(196,168,130,0.15) 0%, transparent 60%), radial-gradient(ellipse at 70% 50%, rgba(139,111,71,0.1) 0%, transparent 60%); }}
  header * {{ position: relative; }}
  .header-tag {{ font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: var(--taupe); margin-bottom: 16px; }}
  h1 {{ font-family: 'Cormorant Garamond', serif; font-size: clamp(38px, 6vw, 64px); font-weight: 300; line-height: 1.1; margin-bottom: 12px; }}
  h1 em {{ font-style: italic; color: var(--taupe); }}
  .header-sub {{ font-size: 14px; color: rgba(245,240,232,0.65); letter-spacing: 1px; margin-bottom: 8px; }}
  .header-stats {{ font-size: 13px; color: var(--taupe); margin-bottom: 28px; letter-spacing: 1px; }}
  .contact-bar {{ display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }}
  .contact-btn {{ display: inline-flex; align-items: center; gap: 8px; padding: 12px 28px; border-radius: 2px; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; text-decoration: none; transition: all 0.25s; cursor: pointer; font-family: 'Jost', sans-serif; }}
  .btn-whatsapp {{ background: #25d366; color: white; }}
  .btn-whatsapp:hover {{ background: #1ebe5d; transform: translateY(-2px); }}
  .btn-email {{ background: transparent; color: var(--cream); border: 1px solid rgba(245,240,232,0.3); }}
  .btn-email:hover {{ border-color: var(--taupe); color: var(--taupe); transform: translateY(-2px); }}
  .notice {{ background: var(--sand); text-align: center; padding: 14px 20px; font-size: 13px; color: var(--dark-brown); letter-spacing: 0.5px; }}
  .notice strong {{ font-weight: 500; }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 20px 24px 80px; }}
  .filter-nav {{ display: flex; gap: 8px; flex-wrap: wrap; padding: 32px 0 24px; border-bottom: 1px solid var(--sand); margin-bottom: 40px; }}
  .filter-btn {{ padding: 8px 20px; border: 1px solid var(--sand); background: transparent; color: var(--text-light); font-family: 'Jost', sans-serif; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; cursor: pointer; border-radius: 2px; transition: all 0.2s; }}
  .filter-btn:hover, .filter-btn.active {{ background: var(--dark-brown); border-color: var(--dark-brown); color: var(--cream); }}
  .category-section {{ margin-bottom: 56px; }}
  .category-title {{ font-family: 'Cormorant Garamond', serif; font-size: 28px; font-weight: 300; color: var(--dark-brown); margin-bottom: 6px; display: flex; align-items: center; gap: 16px; }}
  .category-title::after {{ content: ''; flex: 1; height: 1px; background: var(--sand); }}
  .category-count {{ font-size: 12px; color: var(--text-light); letter-spacing: 1px; margin-bottom: 24px; }}
  .items-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 24px; }}
  .item-card {{ background: white; border: 1px solid var(--sand); border-radius: 4px; overflow: hidden; transition: transform 0.25s, box-shadow 0.25s; position: relative; }}
  .item-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 32px rgba(74,55,40,0.12); }}
  .item-card.sold {{ opacity: 0.6; }}
  .item-img {{ width: 100%; aspect-ratio: 4/3; overflow: hidden; }}
  .item-img img {{ width: 100%; height: 100%; object-fit: cover; }}
  .img-placeholder {{ width: 100%; aspect-ratio: 4/3; background: linear-gradient(135deg, var(--cream) 0%, var(--sand) 100%); display: flex; align-items: center; justify-content: center; color: var(--taupe); font-size: 36px; }}
  .status-badge {{ position: absolute; top: 12px; right: 12px; padding: 4px 10px; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; font-weight: 500; border-radius: 2px; }}
  .badge-available {{ background: var(--available); color: white; }}
  .badge-sold {{ background: var(--sold); color: white; }}
  .badge-reserved {{ background: #d4a017; color: white; }}
  .item-body {{ padding: 16px 18px 18px; }}
  .item-name {{ font-family: 'Cormorant Garamond', serif; font-size: 20px; font-weight: 400; margin-bottom: 4px; color: var(--dark-brown); }}
  .item-desc {{ font-size: 13px; color: var(--text-light); line-height: 1.5; margin-bottom: 12px; }}
  .item-footer {{ display: flex; align-items: center; justify-content: space-between; }}
  .item-price {{ font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 600; color: var(--brown); }}
  .item-price span {{ font-size: 13px; font-weight: 300; color: var(--text-light); }}
  .inquire-btn {{ padding: 7px 16px; background: var(--dark-brown); color: var(--cream); border: none; border-radius: 2px; font-family: 'Jost', sans-serif; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; cursor: pointer; text-decoration: none; display: inline-block; transition: background 0.2s; }}
  .inquire-btn:hover {{ background: var(--brown); }}
  .inquire-btn.disabled {{ background: #ccc; cursor: not-allowed; pointer-events: none; }}
  footer {{ background: var(--dark-brown); color: rgba(245,240,232,0.6); text-align: center; padding: 32px 20px; font-size: 13px; letter-spacing: 0.5px; }}
  footer strong {{ color: var(--taupe); }}
  .updated {{ font-size: 11px; opacity: 0.5; margin-top: 10px; }}
  @media (max-width: 600px) {{
    header {{ padding: 40px 20px 36px; }}
    .items-grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }}
    .item-name {{ font-size: 17px; }}
  }}
</style>
</head>
<body>

<header>
  <p class="header-tag">Dubai · Relocating Sale</p>
  <h1>Everything Must Go<br><em>Quality Home Items</em></h1>
  <p class="header-sub">All items available for viewing in Dubai · Priced to sell fast</p>
  <p class="header-stats">{available_total} of {total} items still available</p>
  <div class="contact-bar">
    <a href="{wa_url_general}" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
    <a href="mailto:{email}?subject=Dubai Home Sale Inquiry" class="contact-btn btn-email">✉ Email</a>
  </div>
</header>

<div class="notice">
  <strong>Pick-up only</strong> · Dubai location shared upon inquiry · Cash &amp; bank transfer accepted
</div>

<main>
  <nav class="filter-nav">
    <button class="filter-btn active" onclick="filterCategory('all', this)">All Items</button>
    <button class="filter-btn" onclick="filterCategory('living', this)">Living Room</button>
    <button class="filter-btn" onclick="filterCategory('bedroom', this)">Bedroom</button>
    <button class="filter-btn" onclick="filterCategory('kitchen', this)">Kitchen &amp; Dining</button>
    <button class="filter-btn" onclick="filterCategory('decor', this)">Decor &amp; Lighting</button>
    <button class="filter-btn" onclick="filterCategory('outdoor', this)">Outdoor</button>
    <button class="filter-btn" onclick="filterCategory('other', this)">Other</button>
  </nav>
{sections_html}
</main>

<footer>
  <p>📍 Dubai · <strong>Pick-up only</strong> · All items sold as-is</p>
  <p style="margin-top:8px;">Questions? <strong>WhatsApp or Email</strong> — responses within a few hours</p>
  <p class="updated">Last updated: {updated}</p>
</footer>

<script>
  function filterCategory(cat, btn) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.category-section').forEach(sec => {{
      sec.style.display = (cat === 'all' || sec.dataset.category === cat) ? '' : 'none';
    }});
  }}
</script>
</body>
</html>'''

if __name__ == "__main__":
    import urllib.parse
    print("🔨 Building Dubai Sale site...")
    items = fetch_items()
    print(f"   Found {len(items)} items")
    html = render_html(items, WHATSAPP_NUMBER, EMAIL, SITE_TITLE)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html generated successfully")
