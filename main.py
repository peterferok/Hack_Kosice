import openai
from base64 import b64decode
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import deepl
import re

OPENAI_API_KEY = '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'
DEEPL_KEY = 'e99c10de-a8be-0424-85e8-3e4a485c0755:fx'
responses = []
detected_language = ''


def insert_narration(image_path, text):
    narration_box_path = 'resources/narrationbox.png'

    # Load the image from file
    narration_image = Image.open(narration_box_path)

    # Create a drawing context
    draw_narration = ImageDraw.Draw(narration_image)

    # Set the font
    font_size = 1
    font = ImageFont.truetype('comic.ttf', font_size)

    # Calculate the maximum text size that will fit in the rectangle
    while draw_narration.multiline_textbbox((0, 0), text, font=font, spacing=8)[3] < 14:
        font_size += 1
        font = ImageFont.truetype('comic.ttf', font_size)

    # Split the text into multiple lines based on the available width and maximum height
    words = text.split()
    lines = ['']

    for word in words:
        if draw_narration.textbbox((0, 0, 512, 512), lines[-1] + ' ' + word, font=font, spacing=8)[2] < 250:
            lines[-1] += ' ' + word
        else:
            lines.append(word)

    # Calculate the bounding box of the text
    bbox = draw_narration.multiline_textbbox((0, 0), '\n'.join(lines), font=font, align='center', spacing=8)

    # Calculate the position to center the text
    x = (narration_image.width - bbox[2] - bbox[0]) / 2 + bbox[0]
    y = (narration_image.height - bbox[3] - bbox[1]) / 2 + bbox[1]

    # Draw the text in a bubble
    draw_narration.multiline_text((x, y), '\n'.join(lines), font=font, fill=(0, 0, 0), align='center', spacing=8)

    panel_image = Image.open(image_path)

    # Create a new image with the combined height of both images and the width of the larger image
    combined_image = Image.new('RGBA', (
        max(panel_image.width, narration_image.width), panel_image.height + narration_image.height))

    # Paste the panel image onto the new image
    combined_image.paste(panel_image, (0, 0))

    # Paste the narration image below the panel image
    combined_image.paste(narration_image, (0, panel_image.height))

    # Save the combined image
    combined_image.save(image_path, 'PNG')


def getImage(prompts, narration, apiKey):
    DATA_DIR = Path.cwd() / "responses"

    DATA_DIR.mkdir(exist_ok=True)

    openai.api_key = apiKey

    response = openai.Image.create(
        prompt=prompts,
        n=5,
        size="256x256",
        response_format="b64_json",
    )

    file_name = DATA_DIR / f"{prompts[:5]}-{response['created']}.json"

    #    with open(file_name, mode="w", encoding="utf-8") as file:
    #        json.dump(response, file)
    images = []
    for index, image_dict in enumerate(response['data']):
        image_data = b64decode(image_dict["b64_json"])
        images.append(image_data)
        image_file = DATA_DIR / f"{file_name.stem}-{index}.png"
        # images[image_file] = image_data
        with open(image_file, mode="wb") as png:
            png.write(image_data)
        insert_narration(image_file, narration)

    return images


def askGPT(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text,
        temperature=0.6,
        max_tokens=500, )
    responses.append(response)
    return (response.choices[0].text)


def translateText(story, main_character):
    translator = deepl.Translator(DEEPL_KEY)
    result = translator.translate_text(story + main_character, target_lang='EN-US')
    translated_text = result.text
    global detected_language
    detected_language = result.detected_source_lang
    return translated_text


def receiveResponse(panel_response):
    panels = []
    panel_pattern = re.compile(r'(\d+):\s*.rt:(.+?)\s*.arration:\s*(.+?)(\n|$)', re.DOTALL)

    for match in panel_pattern.finditer(panel_response):
        print("MATCH\n")
        panel_number = int(match.group(1))
        art = match.group(2).strip()

        narration = match.group(3).strip()
        if detected_language!= 'EN':
            translator = deepl.Translator(DEEPL_KEY)
            narration = translator.translate_text(match.group(3).strip(), target_lang=detected_language)

        panels.append({
            'panel_number': panel_number,
            'art': art,
            'narration': narration,
        })
    return panels


def main():
    Story = "Story: aliens invaded earth\n"
    # Mood="Story mood: Uplifting\n"
    Comic_style = 'manga'
    Main_character = "Main character: Batman\n"

    # translator = deepl.Translator(DEEPL_KEY)
    # result = translator.translate_text(Story+Main_character, target_lang='EN-US')
    # translated_text = result.text
    # detected_language = result.detected_source_lang
    translated_text = translateText(Story, Main_character)
    myQn = "act as professional story writer, your task is to create a coherent captivating complex superhero story plot based on my input: " + "'" + translated_text + "'"
    story_response = askGPT(myQn)

    panel_response = askGPT(
        "Act as a professional comic book writer your task is to create a captivating comic book based on my story. You will divide this book into separate panels, you can make as many panels as the story requires but there have to be at least 6 panels. Your output will look like: \n(panel number) \nArt: (this will be a detailed description of what is happening inside the panel, what characters are there and what is in the background)\nNarration: (description of what is happening in the panel or backstory that led to it)\n\nthe story you are making a comic book for is:\n" + "'" + story_response + "'")
    # panels = []
    # panel_pattern = re.compile(r'Panel (\d+):\s*Art:(.+?)(?=\n\s*\nPanel|$)', re.DOTALL)

    # for match in panel_pattern.finditer(panel_response):
    #    panel_number = int(match.group(1))
    #    art = match.group(2).strip()

    #    panels.append({
    #        'panel_number': panel_number,
    #        'art': art,
    #    })
    for panel in receiveResponse(panel_response):
        getImage(panel['art'] + " in a " + Comic_style + " style no text", panel['narration'], OPENAI_API_KEY)


main()
