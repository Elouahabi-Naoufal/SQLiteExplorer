#!/usr/bin/env python3
"""Create application icon for SQLite Manager"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a simple but professional app icon"""
    # Create a 256x256 image with transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle with gradient effect
    center = size // 2
    radius = 110
    
    # Draw main circle background
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                fill=(41, 128, 185, 255), outline=(52, 152, 219, 255), width=4)
    
    # Draw database cylinder
    cylinder_width = 80
    cylinder_height = 120
    cylinder_x = center - cylinder_width // 2
    cylinder_y = center - cylinder_height // 2
    
    # Cylinder body
    draw.rectangle([cylinder_x, cylinder_y + 15, cylinder_x + cylinder_width, cylinder_y + cylinder_height - 15],
                  fill=(236, 240, 241, 255))
    
    # Top ellipse
    draw.ellipse([cylinder_x, cylinder_y, cylinder_x + cylinder_width, cylinder_y + 30],
                fill=(189, 195, 199, 255))
    
    # Bottom ellipse
    draw.ellipse([cylinder_x, cylinder_y + cylinder_height - 30, cylinder_x + cylinder_width, cylinder_y + cylinder_height],
                fill=(149, 165, 166, 255))
    
    # Add data lines
    for i in range(3):
        y_pos = cylinder_y + 40 + i * 20
        draw.rectangle([cylinder_x + 15, y_pos, cylinder_x + cylinder_width - 15, y_pos + 3],
                      fill=(52, 73, 94, 255))
    
    # Add "SQL" text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "SQL"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = center - text_width // 2
    text_y = center + 50
    
    draw.text((text_x, text_y), text, fill=(44, 62, 80, 255), font=font)
    
    # Save in multiple sizes
    sizes = [16, 32, 48, 64, 128, 256]
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(f'resources/sqlite_manager_{s}.png')
    
    # Save main icon
    img.save('resources/sqlite_manager.png')
    print("App icons created successfully!")

if __name__ == "__main__":
    # Create resources directory if it doesn't exist
    os.makedirs('resources', exist_ok=True)
    create_app_icon()