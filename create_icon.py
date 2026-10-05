from PIL import Image, ImageDraw

def generate_robot_icon(filepath="robot_icon.ico"):
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer glow / background dark circle
    draw.ellipse([8, 8, 248, 248], fill=(3, 16, 8, 255), outline=(0, 255, 102, 255), width=6)

    # Antenna
    draw.line([128, 48, 128, 24], fill=(0, 255, 102, 255), width=6)
    draw.ellipse([118, 14, 138, 34], fill=(255, 255, 255, 255), outline=(0, 255, 102, 255), width=3)

    # Robot Head Box
    draw.rounded_rectangle([44, 52, 212, 172], radius=24, fill=(6, 28, 15, 255), outline=(0, 255, 102, 255), width=5)

    # Ears
    draw.rectangle([30, 88, 44, 136], fill=(0, 255, 102, 255))
    draw.rectangle([212, 88, 226, 136], fill=(0, 255, 102, 255))

    # Visor
    draw.rounded_rectangle([64, 76, 192, 148], radius=14, fill=(2, 8, 4, 255), outline=(0, 180, 70, 255), width=3)

    # Glowing Green Eyes
    draw.ellipse([82, 94, 114, 126], fill=(0, 255, 102, 255))
    draw.ellipse([142, 94, 174, 126], fill=(0, 255, 102, 255))

    # Eye pupils / shine
    draw.ellipse([98, 98, 108, 108], fill=(255, 255, 255, 255))
    draw.ellipse([158, 98, 168, 108], fill=(255, 255, 255, 255))

    # Body preview / neck
    draw.rounded_rectangle([92, 172, 164, 216], radius=10, fill=(8, 35, 20, 255), outline=(0, 255, 102, 255), width=4)
    # Chest light
    draw.ellipse([118, 184, 138, 204], fill=(0, 240, 255, 255))

    # Save as .ico with multiple standard sizes
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(filepath, format="ICO", sizes=sizes)
    print(f"Generated {filepath} successfully.")

if __name__ == "__main__":
    generate_robot_icon()
