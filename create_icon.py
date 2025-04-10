"""
Simple script to create a basic calendar icon for the application.
This creates a simple SVG icon that can be used for the application.
"""
import os

# Create a simple SVG calendar icon
svg_content = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#4285f4" rx="32" ry="32"/>
  <rect x="32" y="64" width="192" height="160" fill="white" rx="8" ry="8"/>
  <rect x="32" y="32" width="192" height="48" fill="#ea4335" rx="8" ry="8"/>
  
  <!-- Calendar grid lines -->
  <line x1="32" y1="112" x2="224" y2="112" stroke="#e0e0e0" stroke-width="2"/>
  <line x1="32" y1="160" x2="224" y2="160" stroke="#e0e0e0" stroke-width="2"/>
  <line x1="80" y1="64" x2="80" y2="224" stroke="#e0e0e0" stroke-width="2"/>
  <line x1="128" y1="64" x2="128" y2="224" stroke="#e0e0e0" stroke-width="2"/>
  <line x1="176" y1="64" x2="176" y2="224" stroke="#e0e0e0" stroke-width="2"/>
  
  <!-- AI symbol -->
  <circle cx="128" cy="140" r="32" fill="#fbbc05" opacity="0.7"/>
  <path d="M112,140 L144,140 M128,124 L128,156" stroke="#4285f4" stroke-width="6" stroke-linecap="round"/>
  
  <!-- Calendar day markers -->
  <text x="56" y="136" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">15</text>
  <text x="104" y="136" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">16</text>
  <text x="152" y="136" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">17</text>
  <text x="200" y="136" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">18</text>
  
  <text x="56" y="184" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">19</text>
  <text x="104" y="184" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">20</text>
  <text x="152" y="184" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">21</text>
  <text x="200" y="184" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#333">22</text>
</svg>'''

# Save the SVG file
svg_path = os.path.join('app', 'static', 'img', 'calendar_icon.svg')
with open(svg_path, 'w') as f:
    f.write(svg_content)

print(f"Created SVG icon at {svg_path}")
