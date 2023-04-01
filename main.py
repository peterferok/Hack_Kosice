from PIL import Image, ImageDraw, ImageFont


def insert_bubble(image_path, text):
    resourcepath = 'resources/' + image_path
    temppath = 'temp/' + image_path

    # Load the image from file
    image = Image.open(resourcepath)

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Set the font
    font_size = 1
    font = ImageFont.truetype('comic.ttf', font_size)

    # Calculate the maximum text size that will fit in the rectangle
    while draw.multiline_textbbox((0, 0), text, font=font, spacing=8)[3] < 70:
        font_size += 1
        font = ImageFont.truetype('comic.ttf', font_size)

    # Split the text into multiple lines based on the available width and maximum height
    words = text.split()
    lines = ['']

    for word in words:
        if draw.textbbox((0, 0, 512, 512), lines[-1] + ' ' + word, font=font, spacing=8)[2] < 470:
            lines[-1] += ' ' + word
        else:
            lines.append(word)

    # Calculate the bounding box of the text
    bbox = draw.multiline_textbbox((0, 0), '\n'.join(lines), font=font, align='center', spacing=8)

    # Calculate the position to center the text
    x = (image.width - bbox[2] - bbox[0]) / 2 + bbox[0]
    y = (image.height - bbox[3] - bbox[1]) / 2 - 70 + bbox[1]

    # Draw the text in a bubble
    draw.multiline_text((x, y), '\n'.join(lines), font=font, fill=(0, 0, 0), align='center', spacing=8)
    image.save(temppath, 'PNG')

insert_bubble('bubble.png', 'everybody!')


