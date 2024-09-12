from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO



def creerImageBVN(member, text: str):
    size = 1024, 500
    size_avatar = 200, 200
  
    reponse = requests.get(member.avatar)
    image_info = BytesIO(reponse.content)
    
    with Image.open(f"Image/{text}.png") as im, Image.open(image_info) as im2:
        
        resized_im = im.resize(size)
        im2 = im2.resize(size_avatar)
        
        mask = Image.new('L', size_avatar, 0)
        masque = ImageDraw.Draw(mask)
        masque.ellipse((0, 0, size_avatar[0], size_avatar[1]), fill=255)
       
        output = ImageOps.fit(im2, size_avatar, centering=(0.5, 0.5))
        output.putalpha(mask)
       
        final_im = resized_im.convert('RGBA')
        avatar_position = ((size[0] - size_avatar[0]) // 2, (size[1] - size_avatar[1]) // 2 - 60)
        final_im.paste(output, avatar_position, mask=output)
       
        texte = ImageDraw.Draw(final_im)
        font = ImageFont.load_default(size=50)
  
        # Obtenir les dimensions du texte
        text_bbox = texte.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
  
        member_bbox = texte.textbbox((0, 0), member.name, font=font)
        member_width = member_bbox[2] - member_bbox[0]


        # Positionner le texte et le membre centrés
        text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2 + 50)
        member_position = ((size[0] - member_width) // 2, text_position[1] + text_height + 10)

        text_color = "white"
        border_color = "black"
        border_width = 2 
             
        # Dessiner les contours du texte et du membre
        for x_offset, y_offset in [(-border_width, 0), (border_width, 0), (0, -border_width), (0, border_width)]:
            texte.text((text_position[0] + x_offset, text_position[1] + y_offset), text, font=font, fill=border_color)
            texte.text((member_position[0] + x_offset, member_position[1] + y_offset), member.name, font=font, fill=border_color)

        # Dessiner le texte principal et le membre
        texte.text(text_position, text, font=font, fill=text_color)
        texte.text(member_position, member.name, font=font, fill=text_color)

        return final_im
    

