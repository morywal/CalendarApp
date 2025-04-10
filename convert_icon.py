"""
Script to convert SVG icon to ICO format for Windows executable
"""
import os
from cairosvg import svg2png
from PIL import Image

def svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Convert SVG to ICO with multiple sizes"""
    # Create a temporary directory for PNG files
    temp_dir = 'temp_icons'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Convert SVG to multiple PNG sizes
    png_files = []
    for size in sizes:
        png_path = os.path.join(temp_dir, f'icon_{size}.png')
        svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
        png_files.append(png_path)
    
    # Create ICO file with all sizes
    images = [Image.open(png_file) for png_file in png_files]
    images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    # Clean up temporary files
    for png_file in png_files:
        os.remove(png_file)
    os.rmdir(temp_dir)
    
    print(f"Created ICO file at {ico_path}")

if __name__ == "__main__":
    svg_path = os.path.join('app', 'static', 'img', 'calendar_icon.svg')
    ico_path = os.path.join('app', 'static', 'img', 'calendar_icon.ico')
    svg_to_ico(svg_path, ico_path)
