import numpy as np
from PIL import Image
import random
image1 = Image.open('batman.png')

image2 = Image.open('bubble.png')
new_image = image2.resize((75, 75))
new_pos = (random.randint(25,200),random.randint(25,75)) 
image1.paste(new_image,new_pos,new_image)
image1.save('pasted_image.jpg')