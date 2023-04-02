from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

import json
import os
from pathlib import Path
import openai
import json
from base64 import b64decode
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import deepl
from diffusers import StableDiffusionImageVariationPipeline
import torch
from torchvision import transforms
import re
import base64
import requests

OPENAI_API_KEY = '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'
DEEPL_KEY = 'e99c10de-a8be-0424-85e8-3e4a485c0755:fx'
responses = []


# Create your views here.
class HomeView(LoginRequiredMixin, View):
    login_url = '/account'
    
    def get(self, request):
        return render(request, "main/home.html", {})
    
    def post(self, request):
        story = request.POST.get('story')
        hero = request.POST.get('hero')
        style = request.POST.get('style')

        prompt = None

        index = int(request.POST.get('index'))
        if index == None:
            index = 0

        panels = request.POST.get('panels')
        if panels == None:
            panels = main(story, style, hero)
        
        for _ in range(5):
            print(index)
            print(type(index))
            data, prompt = getImage(panels[0]['art']+" in a "+style+" style no text",OPENAI_API_KEY)
            
            img_data = requests.get(data).content
            with open('~/../account/static/account/img/current' + str(i) + '.jpg', 'wb') as handler:
                handler.write(img_data)
        
        return render(request, "main/images.html", {'prompt': prompt, 'index': index, 'panels': panels})
    

class ImagesView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "main/images.html", {})
        

def getImage(prompts,apiKey):
    DATA_DIR = Path.cwd() / "responses"

    DATA_DIR.mkdir(exist_ok=True)

    openai.api_key = apiKey

    response = openai.Image.create(
        prompt=prompts,
        n=1,
        size="256x256"
    )
    print("ajajajaj")
    print(prompts)

    #file_name = DATA_DIR / f"{prompts[:1]}-{response['created']}.json"

#    with open(file_name, mode="w", encoding="utf-8") as file:
#        json.dump(response, file)
   
    #for index, image_dict in enumerate(response['data']):
    #    image_data = b64decode(image_dict["b64_json"])
    #    image = image_data
        #image_file = DATA_DIR / f"{file_name.stem}-{index}.png"
        #images[image_file] = image_data
        #with open(image_file, mode="wb") as png:
        #    png.write(image_data)

    return response["data"][0]["url"], prompts


def askGPT(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
    engine = "text-davinci-003",
    prompt = text,
    temperature = 0.6,
    max_tokens = 500,)
    responses.append(response)
    return (response.choices[0].text)


def translateText(story,main_character):
    translator = deepl.Translator(DEEPL_KEY)
    result = translator.translate_text(story+main_character, target_lang='EN-US')
    translated_text = result.text
    detected_language = result.detected_source_lang
    return translated_text


def receiveResponse(panel_response):
    panels = []
    panel_pattern = re.compile(r'Panel (\d+):\s*Art:(.+?)(?=\n\s*\nPanel|$)', re.DOTALL)
    
    for match in panel_pattern.finditer(panel_response):
        panel_number = int(match.group(1))
        art = match.group(2).strip()
    
        panels.append({
            'panel_number': panel_number,
            'art': art,
        })
    return panels



def main(Story,Comic_style,Main_character):
    #Story="Story: aliens invaded earth\n"
    #Mood="Story mood: Uplifting\n"
    #Comic_style = 'manga\n'
    #Main_character="Main character: Batman\n"
    
    #translator = deepl.Translator(DEEPL_KEY)
    #result = translator.translate_text(Story+Main_character, target_lang='EN-US')
    #translated_text = result.text
    #detected_language = result.detected_source_lang
    translated_text = translateText(Story,Main_character)
    myQn = "act as professional story writer, your task is to create a coherent captivating complex superhero story plot based on my input: "+ "'"+translated_text+"'"
    story_response=askGPT(myQn)
    
    panel_response=askGPT("Act as a professional comic book writer your task is to create a captivating comic book based on my story. You will divide this book into separate panels, you can make as many panels as the story requires but there have to be at least 5 panels. Your output will look like: \n(panel number) \nArt: (this will be a detailed description of what is happening inside the panel, what characters are there and what is in the background)\n\nthe story you are making a comic book for is:\n"+"'"+story_response+"'")
    #panels = []
    #panel_pattern = re.compile(r'Panel (\d+):\s*Art:(.+?)(?=\n\s*\nPanel|$)', re.DOTALL)
    
    #for match in panel_pattern.finditer(panel_response):
    #    panel_number = int(match.group(1))
    #    art = match.group(2).strip()
    
    #    panels.append({
    #        'panel_number': panel_number,
    #        'art': art,
    #    })
    return receiveResponse(panel_response)