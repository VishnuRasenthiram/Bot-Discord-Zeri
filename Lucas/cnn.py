from PIL import Image
from waifu2x_ncnn_py import Waifu2x

waifu2x = Waifu2x(gpuid=-1, scale=1, noise=2)
with Image.open("grosImage.jpg") as image:
    image = waifu2x.process_pil(image)
    image.save("output.jpg", quality=95)