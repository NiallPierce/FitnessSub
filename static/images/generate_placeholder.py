from PIL import Image, ImageDraw, ImageFont

# Create a new image with a light gray background
img = Image.new('RGB', (200, 200), color='#f0f0f0')
d = ImageDraw.Draw(img)

# Try to use Arial font, fallback to default if not available
try:
    font = ImageFont.truetype("arial.ttf", 20)
except IOError:
    font = ImageFont.load_default()

# Add "No Image" text
text = "No Image"
text_bbox = d.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
x = (200 - text_width) / 2
y = (200 - text_height) / 2

d.text((x, y), text, fill='#666666', font=font)

# Save the image
img.save('no-image.png')
print("Generated no-image.png successfully!")
