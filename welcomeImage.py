from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO



def creerImage(member, text: str):
    size = 1024, 500
    size_avatar = 200, 200
  
    reponse = requests.get(member.avatar)
    print("1")
    image_info = BytesIO(reponse.content)
    with Image.open(f"Image/{text}.png") as im, Image.open(image_info) as im2:
        print("1")
        resized_im = im.resize(size)
        im2 = im2.resize(size_avatar)
        
        mask = Image.new('L', size_avatar, 0)
        masque = ImageDraw.Draw(mask)
        masque.ellipse((0, 0, size_avatar[0], size_avatar[1]), fill=255)
        print("2")
        output = ImageOps.fit(im2, size_avatar, centering=(0.5, 0.5))
        output.putalpha(mask)
        print("3")
        final_im = resized_im.convert('RGBA')
        avatar_position = ((size[0] - size_avatar[0]) // 2, (size[1] - size_avatar[1]) // 2 - 60)
        final_im.paste(output, avatar_position, mask=output)
        print("4")
        texte = ImageDraw.Draw(final_im)
        font = ImageFont.truetype(size=50)
        print("5")
        # Obtenir les dimensions du texte
        text_bbox = texte.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        print("6")
        member_bbox = texte.textbbox((0, 0), member.name, font=font)
        member_width = member_bbox[2] - member_bbox[0]

        print("7")
        # Positionner le texte et le membre centrés
        text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2 + 50)
        member_position = ((size[0] - member_width) // 2, text_position[1] + text_height + 10)
        print("8")
        text_color = "white"
        border_color = "black"
        border_width = 2 
             
        # Dessiner les contours du texte et du membre
        for x_offset, y_offset in [(-border_width, 0), (border_width, 0), (0, -border_width), (0, border_width)]:
            texte.text((text_position[0] + x_offset, text_position[1] + y_offset), text, font=font, fill=border_color)
            texte.text((member_position[0] + x_offset, member_position[1] + y_offset), member.name, font=font, fill=border_color)
        print("9")
        # Dessiner le texte principal et le membre
        texte.text(text_position, text, font=font, fill=text_color)
        texte.text(member_position, member.name, font=font, fill=text_color)
        print("10")
        return final_im
    

