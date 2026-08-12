#!/usr/bin/env python3
"""
Banner Generator for kesaruhasun GitHub Profile
Generates animated terminal banner SVGs (dark.svg & light.svg).
Uses Floyd-Steinberg dithering for portrait and proper monospace text layout.
"""

import os
import sys
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def create_dither_matrix(width, height, image_path=None, is_dark=True):
    """
    Creates a dithered dot grid from an image using Floyd-Steinberg with serpentine scan.
    For dark mode: background segmented out, subject drawn in dots.
    For light mode: background kept, dark areas drawn in dots.
    """
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path).convert('RGBA')
        
        # Smart crop: find center of image, crop head-and-shoulders
        w_orig, h_orig = img.size
        # Target aspect ratio for our frame
        target_aspect = width / height  # ~0.88
        current_aspect = w_orig / h_orig
        
        if current_aspect > target_aspect:
            # Image is wider than target — crop sides
            new_w = int(h_orig * target_aspect)
            left = (w_orig - new_w) // 2
            img = img.crop((left, 0, left + new_w, h_orig))
        else:
            # Image is taller than target — crop bottom
            new_h = int(w_orig / target_aspect)
            img = img.crop((0, 0, w_orig, new_h))
        
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        gray = img.convert('L')
        
        # Apply 1.3x contrast boost as per spec
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.3)
        
        # Unsharp mask for edge crispness
        gray = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
        
        img_np = np.array(gray, dtype=float)
        
        if is_dark:
            # Dark mode: invert so dark subject areas become dots (white=dot)
            # We want the person/dark areas to show as dots on dark background
            pass  # Keep as-is: dark pixels -> low values -> will become dots (new_val=0 -> dithered=1)
        else:
            # Light mode: invert the image so light background areas become dots
            img_np = 255.0 - img_np
    else:
        # Generate a stylized placeholder silhouette
        img_np = np.full((height, width), 230.0)
        y, x = np.ogrid[:height, :width]
        cx, cy = width // 2, height // 3
        
        # Head oval
        head_mask = ((x - cx)**2 / (width*0.22)**2 + (y - cy)**2 / (height*0.22)**2) <= 1.0
        # Neck
        neck_mask = ((np.abs(x - cx) < width*0.08) & (y > cy + height*0.18) & (y < cy + height*0.32))
        # Shoulders
        shoulder_cy = cy + height*0.4
        shoulder_mask = ((x - cx)**2 / (width*0.45)**2 + (y - shoulder_cy)**2 / (height*0.25)**2) <= 1.0
        shoulder_mask = shoulder_mask & (y > cy + height*0.25)
        
        img_np[shoulder_mask] = 70.0
        img_np[neck_mask] = 65.0
        img_np[head_mask] = 55.0
        
        # Subtle gradient
        gradient = np.linspace(0.85, 1.15, height)[:, None]
        img_np = np.clip(img_np * gradient, 0, 255)
    
    # Floyd-Steinberg Dithering with serpentine scan
    h, w = img_np.shape
    dithered = np.zeros((h, w), dtype=int)
    work = img_np.copy()
    
    for y_idx in range(h):
        reverse = (y_idx % 2 == 1)
        x_range = range(w - 1, -1, -1) if reverse else range(w)
        for x_idx in x_range:
            old_val = work[y_idx, x_idx]
            new_val = 255.0 if old_val > 128.0 else 0.0
            dithered[y_idx, x_idx] = 1 if new_val == 0 else 0
            err = old_val - new_val
            
            if not reverse:
                if x_idx + 1 < w:
                    work[y_idx, x_idx + 1] += err * 7.0 / 16.0
                if y_idx + 1 < h:
                    if x_idx - 1 >= 0:
                        work[y_idx + 1, x_idx - 1] += err * 3.0 / 16.0
                    work[y_idx + 1, x_idx] += err * 5.0 / 16.0
                    if x_idx + 1 < w:
                        work[y_idx + 1, x_idx + 1] += err * 1.0 / 16.0
            else:
                if x_idx - 1 >= 0:
                    work[y_idx, x_idx - 1] += err * 7.0 / 16.0
                if y_idx + 1 < h:
                    if x_idx + 1 < w:
                        work[y_idx + 1, x_idx + 1] += err * 3.0 / 16.0
                    work[y_idx + 1, x_idx] += err * 5.0 / 16.0
                    if x_idx - 1 >= 0:
                        work[y_idx + 1, x_idx - 1] += err * 1.0 / 16.0
    
    return dithered


def xml_escape(s):
    """Escape special characters for XML."""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_banner_svg(is_dark=True, image_path=None):
    """Generate a single banner SVG file."""
    
    W, H = 1180, 610
    
    # ── Color palette ──
    if is_dark:
        bg          = "#0A101F"
        card_bg     = "#0F172A"
        border      = "#1E293B"
        chrome_txt  = "#94A3B8"
        cyan        = "#22D3EE"
        green       = "#10B981"
        purple      = "#A78BFA"
        muted       = "#64748B"
        label_col   = "#38BDF8"
        val_col     = "#CBD5E1"
    else:
        bg          = "#F8FAFC"
        card_bg     = "#FFFFFF"
        border      = "#E2E8F0"
        chrome_txt  = "#475569"
        cyan        = "#0891B2"
        green       = "#059669"
        purple      = "#7C3AED"
        muted       = "#94A3B8"
        label_col   = "#0284C7"
        val_col     = "#1E293B"

    # ── Dither portrait ──
    dither_w, dither_h = 280, 320
    dither = create_dither_matrix(dither_w, dither_h, image_path, is_dark)

    # Convert to SVG dot paths — each dot is a 1.2×1.2 rect
    frame_x, frame_y = 52, 126
    dot_size = 1.15
    dots = []
    for r in range(dither_h):
        for c in range(dither_w):
            if dither[r, c] == 1:
                px = frame_x + c * dot_size
                py = frame_y + r * dot_size
                dots.append(f"M{px:.1f},{py:.1f}h{dot_size}v{dot_size}h-{dot_size}z")
    portrait_path = " ".join(dots)

    # ── System info rows ──
    # Keep values SHORT so they don't overflow the panel
    rows = [
        ("Subject",   "Kesaru Hasun Dhanasinghe"),
        ("Role",      "AI Systems Dev · Tekkeys Co-founder"),
        ("Origin",    "Colombo, Sri Lanka"),
        ("Education", "BSc IT (AI/DS) @ SLIIT"),
        ("Status",    "Building OpenClaw · Shipping Agents"),
        ("Tools",     "Obsidian · MCP · Docker · Linux"),
        ("Lang",      "Python · TypeScript · Java · SQL"),
        ("Frontend",  "Next.js 15 · React · Tailwind CSS"),
        ("Backend",   "Node.js · FastAPI · CF Workers"),
        ("Data",      "Postgres · Cloudflare D1 · VectorDBs"),
        ("Infra",     "GCP · Anthropic CPN · Vercel"),
        ("Certs",     "GenAI Cohort 2 · DeepMind SLM"),
        ("Web",       "kesaru.me · sobersided.com"),
        ("GitHub",    "github.com/kesaruhasun"),
    ]

    # Right panel starts at x=435, width=705, so content area ~450 to ~1120 = 670px
    # We use a simple two-column layout: label at fixed x, value at fixed x
    panel_x = 452
    label_x = panel_x + 8
    value_x = panel_x + 140  # After label + dots
    start_y = 155
    row_h = 26
    font_size = 12.5

    info_svg_parts = []
    for i, (label, val) in enumerate(rows):
        y = start_y + i * row_h
        val_esc = xml_escape(val)
        # Dotted leader between label and value
        dot_count = max(2, 16 - len(label))
        leader = "·" * dot_count
        info_svg_parts.append(
            f'    <text x="{label_x}" y="{y}" fill="{label_col}" '
            f'font-family="\'JetBrains Mono\',Menlo,Monaco,\'Courier New\',monospace" '
            f'font-size="{font_size}" font-weight="700">{xml_escape(label)}</text>\n'
            f'    <text x="{label_x + 95}" y="{y}" fill="{muted}" '
            f'font-family="\'JetBrains Mono\',Menlo,Monaco,\'Courier New\',monospace" '
            f'font-size="{font_size}" letter-spacing="1">{leader}</text>\n'
            f'    <text x="{value_x}" y="{y}" fill="{val_col}" '
            f'font-family="\'JetBrains Mono\',Menlo,Monaco,\'Courier New\',monospace" '
            f'font-size="{font_size}">{val_esc}</text>'
        )
    info_rows_block = "\n".join(info_svg_parts)

    # ── Build SVG ──
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <style>
      @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
      }}
      .live-dot {{ animation: pulse 2s ease-in-out infinite; }}
    </style>
    <clipPath id="termClip"><rect x="20" y="62" width="1140" height="528" rx="0"/></clipPath>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" fill="{bg}" rx="16"/>

  <!-- Terminal Window -->
  <rect x="20" y="20" width="1140" height="570" fill="{card_bg}" stroke="{border}" stroke-width="1.5" rx="12"/>

  <!-- Title Bar -->
  <rect x="20" y="20" width="1140" height="42" fill="{border}" rx="12"/>
  <rect x="20" y="50" width="1140" height="12" fill="{border}"/>
  <!-- Traffic lights -->
  <circle cx="48" cy="41" r="6" fill="#EF4444"/>
  <circle cx="68" cy="41" r="6" fill="#F59E0B"/>
  <circle cx="88" cy="41" r="6" fill="#10B981"/>
  <!-- Title text -->
  <text x="590" y="46" fill="{chrome_txt}" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="13" font-weight="600" text-anchor="middle">profile.sh --live</text>
  <!-- LIVE badge -->
  <g transform="translate(1020, 31)">
    <rect width="100" height="22" fill="#EF4444" fill-opacity="0.15" stroke="#EF4444" stroke-width="1" rx="11"/>
    <circle cx="15" cy="11" r="4" fill="#EF4444" class="live-dot"/>
    <text x="26" y="15" fill="#EF4444" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="10" font-weight="700">LIVE SYSTEM</text>
  </g>

  <!-- ═══════════ LEFT PANEL: VISUAL.MAP ═══════════ -->
  <rect x="30" y="72" width="395" height="508" fill="{bg}" stroke="{border}" stroke-width="1" rx="8"/>
  <!-- Panel header -->
  <rect x="30" y="72" width="395" height="28" fill="{border}" rx="8"/>
  <rect x="30" y="92" width="395" height="8" fill="{border}"/>
  <text x="44" y="91" fill="{cyan}" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="11" font-weight="700">VISUAL.MAP // DITHER_MATRIX</text>

  <!-- Dithered Portrait -->
  <g clip-path="url(#termClip)">
    <path d="{portrait_path}" fill="{purple}" shape-rendering="crispEdges"/>
  </g>

  <!-- ═══════════ RIGHT PANEL: SYSTEM.INFO ═══════════ -->
  <rect x="435" y="72" width="715" height="508" fill="{bg}" stroke="{border}" stroke-width="1" rx="8"/>
  <!-- Panel header -->
  <rect x="435" y="72" width="715" height="28" fill="{border}" rx="8"/>
  <rect x="435" y="92" width="715" height="8" fill="{border}"/>
  <text x="450" y="91" fill="{green}" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="11" font-weight="700">SYSTEM.INFO // KESARU_HASUN_DHANASINGHE</text>

  <!-- Username pill -->
  <g transform="translate(990, 76)">
    <rect width="148" height="20" fill="{cyan}" fill-opacity="0.15" stroke="{cyan}" stroke-width="1" rx="10"/>
    <text x="74" y="14" fill="{cyan}" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="10" font-weight="700" text-anchor="middle">@kesaruhasun</text>
  </g>

  <!-- Info Rows -->
{info_rows_block}

  <!-- Bottom status bar -->
  <line x1="435" y1="540" x2="1150" y2="540" stroke="{border}" stroke-width="1"/>
  <text x="450" y="560" fill="{muted}" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="11">● Tekkeys Co-founder &amp; AI Systems Architect</text>
  <text x="930" y="560" fill="{green}" font-family="'JetBrains Mono',Menlo,Monaco,'Courier New',monospace" font-size="11">GenAI Cohort 2 ⚡</text>
</svg>'''

    fname = "dark.svg" if is_dark else "light.svg"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✓ Generated {fname} ({len(dots)} dots)")


if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else None
    generate_banner_svg(is_dark=True, image_path=img)
    generate_banner_svg(is_dark=False, image_path=img)
    print("Done!")
