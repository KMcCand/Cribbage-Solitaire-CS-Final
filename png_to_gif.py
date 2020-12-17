from PIL import Image
import os

count = -1

for file in os.listdir("PNG"):
    if file.endswith(".png"):
        count += 1
    
        im = Image.open(os.path.join("PNG", file))
        # Get the alpha band
        alpha = im.split()[3]

        # Convert the image into P mode but only use 255 colors in the palette out of 256
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)

        # Set all pixel values below 128 to 255,
        # and the rest to 0
        mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)

        # Paste the color of index 255 and use alpha as a mask
        im.paste(255, mask)
        # The transparency index is 255
        im.save(f'GIF/{file[:-4]}.gif', transparency=255)