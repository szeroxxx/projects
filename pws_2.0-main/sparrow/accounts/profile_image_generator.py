# -*- coding: utf-8 -*-

# ------------------------------------ Imports ----------------------------------#

# Import operating system lib
import os

# Import random generator
from random import shuffle

from django.conf import settings

# Import python imaging libs
from PIL import Image, ImageColor, ImageDraw, ImageFont

from base.util import Util

# ------------------------------ Generate Characters ----------------------------#


def GenerateCharacters(characters, id):
    # Directory containing fonts

    font_resource_file = os.path.join(settings.BASE_DIR, "base", "static", "base", "fonts", "OpenSans-Bold.ttf")
    print(font_resource_file)
    # ------------------------------------ Characters -------------------------------#

    # ------------------------------------- Colors ----------------------------------#

    background_colors = [
        "#f44336",
        "#E91E63",
        "#9C27B0",
        "#673AB7",
        "#3F51B5",
        "#2196F3",
        "#03A9F4",
        "#00BCD4",
        "#009688",
        "#4CAF50",
        "#8BC34A",
        "#CDDC39",
        "#FFC107",
        "#FF9800",
        "#FF5722",
    ]

    # -------------------------------------- Sizes ----------------------------------#

    font_size = 50

    # Image size
    image_size = 100
    shuffle(background_colors)
    color = background_colors[3]
    background_color = ImageColor.getrgb(color)
    if font_size > 0:
        # For each background color do
        # for background_color in background_colors:
        # Convert the character into unicode
        character = characters.upper()

        # Create character image :
        # Grayscale, image size, background color
        char_image = Image.new("RGB", (image_size, image_size), background_color)

        # Draw character image
        draw = ImageDraw.Draw(char_image)

        # Specify font : Resource file, font size
        font = ImageFont.truetype(font_resource_file, size=font_size)

        # Get character width and height
        (font_width, font_height) = font.getsize(character)

        # Calculate x position
        x = (image_size - font_width) / 2

        # Calculate y position
        y = (image_size - font_height) / 3

        # Draw text : Position, String,
        # Options = Fill color, Font
        draw.text((x, y), character, 245 - 255, font=font)

        # Save image
        file_name = "profile_" + str(id) + ".png"

        resource_path = Util.get_resource_path("profile", "")
        if not os.path.exists(resource_path):
            os.makedirs(resource_path)
        file_path = os.path.join(resource_path, file_name)
        char_image.save(file_path)

    return file_name


# ---------------------------------- Input and Output ---------------------------#
