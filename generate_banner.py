#!/usr/bin/env python3
"""
Banner Generator for kesaruhasun GitHub Profile
Generates animated terminal banner SVGs (dark.svg & light.svg) adhering to GitHub-Profile-Master-Prompt specs.
Supports input image dithering via PIL and NumPy.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def create_dither_matrix(width=300, height=340, image_path=None):
    """
    Creates a 300x340 1-bit Floyd-Steinberg dithered grid.
    If image_path is provided, processes the photo; otherwise generates a tech portrait silhouette matrix.
    """
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path).convert('L')
        # Crop head & shoulders if needed, resize to width x height
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        # Apply contrast 1.3x & unsharp mask as per spec
        img = ImageOps.autocontrast(img, cutoff=1)
        img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
        img_np = np.array(img, dtype=float)
    else:
        # Generate a stylized portrait silhouette / geometric tech face pattern
        img_np = np.full((height, width), 240.0)
        y, x = np.ogrid[:height, :width]
        
        # Head oval
        head_mask = ((x - 150)**2 / 75**2 + (y - 130)**2 / 95**2) <= 1.0
        # Shoulders arc
        shoulder_mask = ((x - 150)**2 / 140**2 + (y - 280)**2 / 100**2) <= 1.0
        # Glasses / Tech highlight
        eyes_mask = ((np.abs(x - 150) > 20) & (np.abs(x - 150) < 60) & (np.abs(y - 120) < 18))
        
        img_np[shoulder_mask] = 80.0
        img_np[head_mask] = 60.0
        img_np[eyes_mask] = 220.0
        
        # Add subtle noise/shading gradient
        gradient = np.linspace(0.8, 1.2, height)[:, None]
        img_np = np.clip(img_np * gradient, 0, 255)
    
    # Floyd-Steinberg Dithering with serpentine scan
    h, w = img_np.shape
    dithered = np.zeros((h, w), dtype=int)
    work = img_np.copy()
    
    for y in range(h):
        reverse = (y % 2 == 1)
        x_range = range(w - 1, -1, -1) if reverse else range(w)
        for x in x_range:
            old_val = work[y, x]
            new_val = 255 if old_val > 128 else 0
            dithered[y, x] = 1 if new_val == 0 else 0
            err = old_val - new_val
            
            if not reverse:
                if x + 1 < w: work[y, x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0: work[y + 1, x - 1] += err * 3 / 16
                    work[y + 1, x] += err * 5 / 16
                    if x + 1 < w: work[y + 1, x + 1] += err * 1 / 16
            else:
                if x - 1 >= 0: work[y, x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w: work[y + 1, x + 1] += err * 3 / 16
                    work[y + 1, x] += err * 5 / 16
                    if x - 1 >= 0: work[y + 1, x - 1] += err * 1 / 16
                    
    return dithered

def generate_banner_svg(is_dark=True, image_path=None):
    width, height = 1180, 610
    
    # Colors according to Master Prompt Spec
    if is_dark:
        bg_color = "#0A101F"
        card_bg = "#0F172A"
        card_border = "#1E293B"
        chrome_title = "#94A3B8"
        ui_primary = "#22D3EE"
        accent_color = "#10B981"
        portrait_color = "#A78BFA"
        text_muted = "#64748B"
        text_main = "#E2E8F0"
        label_color = "#38BDF8"
        value_color = "#F8FAFC"
    else:
        bg_color = "#F8FAFC"
        card_bg = "#FFFFFF"
        card_border = "#E2E8F0"
        chrome_title = "#475569"
        ui_primary = "#0891B2"
        accent_color = "#059669"
        portrait_color = "#7C3AED"
        text_muted = "#94A3B8"
        text_main = "#0F172A"
        label_color = "#0284C7"
        value_color = "#0F172A"

    dither_matrix = create_dither_matrix(300, 340, image_path)
    
    # Convert dither matrix to SVG path rects/dots
    dot_paths = []
    frame_x, frame_y = 45, 140
    scale_x, scale_y = 1.2, 1.2
    
    for r in range(dither_matrix.shape[0]):
        for c in range(dither_matrix.shape[1]):
            if dither_matrix[r, c] == 1:
                dx = frame_x + c * scale_x
                dy = frame_y + r * scale_y
                dot_paths.append(f"M{dx:.1f},{dy:.1f}h1v1h-1z")
                
    portrait_d = " ".join(dot_paths)

    # Info panel data updated with exact developer context
    rows = [
        ("Subject", "Kesaru Hasun Dhanasinghe"),
        ("Role", "AI Systems Dev & Tekkeys Co-founder"),
        ("Origin", "Colombo, Sri Lanka"),
        ("Education", "BSc (Hons) IT (AI/Data Science) @ SLIIT"),
        ("Status", "Building OpenClaw + Shipping AI Agents"),
        ("ToolChain", "Obsidian · Spokenly · MCP · Docker · Linux"),
        ("Core.Lang", "Python · TypeScript · Java · SQL · PHP"),
        ("Core.Front", "Next.js 15 · React · Tailwind CSS"),
        ("Core.Back", "Node.js · FastAPI · Cloudflare Workers"),
        ("Core.Data", "PostgreSQL · Cloudflare D1 · Vector DBs"),
        ("Core.Infra", "GCP · Anthropic CPN · Vercel · Firebase"),
        ("Certifications", "Google GenAI Cohort 2 · DeepMind SLM · MCP"),
        ("Grid.Web", "https://kesaru.me · https://sobersided.com"),
        ("Grid.GitHub", "github.com/kesaruhasun"),
    ]

    info_rows_svg = []
    start_y = 175
    row_height = 27
    
    for i, (label, val) in enumerate(rows):
        y_pos = start_y + i * row_height
        dots_count = max(2, 28 - len(label))
        dots_str = "." * dots_count
        val_xml = val.replace('&', '&amp;')
        
        info_rows_svg.append(f'''
        <g transform="translate(450, {y_pos})">
            <text x="0" y="0" fill="{label_color}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="13" font-weight="bold">{label}</text>
            <text x="110" y="0" fill="{text_muted}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="13">{dots_str}</text>
            <text x="210" y="0" fill="{value_color}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="13" font-weight="500" textLength="470" lengthAdjust="spacingAndGlyphs">{val_xml}</text>
        </g>
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.4; transform: scale(0.85); }}
            }}
            @keyframes morphLogo {{
                0%, 20% {{ transform: translate(0px, 0px) scale(1); opacity: 0.9; }}
                25%, 45% {{ transform: translate(10px, -5px) scale(1.05); opacity: 0.6; }}
                50%, 70% {{ transform: translate(-5px, 5px) scale(0.95); opacity: 0.9; }}
                75%, 100% {{ transform: translate(0px, 0px) scale(1); opacity: 0.9; }}
            }}
            .live-dot {{
                animation: pulse 2s infinite ease-in-out;
                transform-origin: 1060px 48px;
            }}
            .morph-logo {{
                animation: morphLogo 14.2s infinite ease-in-out;
            }}
        </style>
    </defs>

    <!-- Main Background -->
    <rect width="{width}" height="{height}" fill="{bg_color}" rx="16"/>

    <!-- Terminal Window Container -->
    <rect x="20" y="20" width="1140" height="570" fill="{card_bg}" stroke="{card_border}" stroke-width="2" rx="12"/>

    <!-- Terminal Header Bar -->
    <rect x="20" y="20" width="1140" height="42" fill="{card_border}" rx="12"/>
    <rect x="20" y="50" width="1140" height="12" fill="{card_border}"/>

    <!-- Window Controls -->
    <circle cx="48" cy="41" r="6" fill="#EF4444"/>
    <circle cx="68" cy="41" r="6" fill="#F59E0B"/>
    <circle cx="88" cy="41" r="6" fill="#10B981"/>

    <!-- Window Title -->
    <text x="590" y="46" fill="{chrome_title}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="13" font-weight="bold" text-anchor="middle">profile.sh --live</text>

    <!-- Pulsing LIVE Badge -->
    <g transform="translate(1010, 31)">
        <rect x="0" y="0" width="110" height="22" fill="#EF4444" fill-opacity="0.15" stroke="#EF4444" stroke-width="1" rx="11"/>
        <circle cx="16" cy="11" r="4" fill="#EF4444" class="live-dot"/>
        <text x="28" y="15" fill="#EF4444" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="11" font-weight="bold">LIVE SYSTEM</text>
    </g>

    <!-- Left Frame: VISUAL.MAP Portrait & Logo Morph -->
    <rect x="40" y="80" width="375" height="485" fill="{bg_color}" stroke="{card_border}" stroke-width="1.5" rx="8"/>
    <rect x="40" y="80" width="375" height="30" fill="{card_border}" rx="8"/>
    <rect x="40" y="102" width="375" height="8" fill="{card_border}"/>
    <text x="55" y="100" fill="{ui_primary}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="12" font-weight="bold">VISUAL.MAP // DITHER_MATRIX</text>

    <!-- Dither Portrait Dots -->
    <path d="{portrait_d}" fill="{portrait_color}" shape-rendering="crispEdges"/>

    <!-- Morphing Logo Overlays -->
    <g class="morph-logo" transform="translate(320, 480)">
        <rect x="0" y="0" width="75" height="65" fill="{card_bg}" stroke="{ui_primary}" stroke-width="1.5" rx="8"/>
        <polygon points="37.5,15 57.5,50 17.5,50" fill="{accent_color}"/>
    </g>

    <!-- Right Frame: SYSTEM.INFO Readout -->
    <rect x="435" y="80" width="705" height="485" fill="{bg_color}" stroke="{card_border}" stroke-width="1.5" rx="8"/>
    <rect x="435" y="80" width="705" height="30" fill="{card_border}" rx="8"/>
    <rect x="435" y="102" width="705" height="8" fill="{card_border}"/>
    <text x="450" y="100" fill="{accent_color}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="12" font-weight="bold">SYSTEM.INFO // KESARU_HASUN_DHANASINGHE</text>

    <!-- Username Pill -->
    <g transform="translate(980, 84)">
        <rect x="0" y="0" width="145" height="22" fill="{ui_primary}" fill-opacity="0.2" stroke="{ui_primary}" stroke-width="1" rx="6"/>
        <text x="72" y="15" fill="{ui_primary}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="11" font-weight="bold" text-anchor="middle">@kesaruhasun</text>
    </g>

    <!-- Info Rows -->
    {"".join(info_rows_svg)}

    <!-- Bottom Terminal Status Bar -->
    <line x1="435" y1="525" x2="1140" y2="525" stroke="{card_border}" stroke-width="1.5"/>
    <text x="450" y="548" fill="{text_muted}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="11">● Tekkeys Co-founder &amp; AI Systems Architect</text>
    <text x="910" y="548" fill="{accent_color}" font-family="Menlo, Monaco, 'Courier New', monospace" font-size="11">Google Cloud GenAI Cohort 2 ⚡</text>
</svg>'''

    filename = "dark.svg" if is_dark else "light.svg"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {filename} successfully.")

if __name__ == "__main__":
    img_arg = sys.argv[1] if len(sys.argv) > 1 else None
    generate_banner_svg(is_dark=True, image_path=img_arg)
    generate_banner_svg(is_dark=False, image_path=img_arg)
