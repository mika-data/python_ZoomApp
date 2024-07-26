from PIL import Image
from config import Config

class ImageModel:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img_pil = Image.open(image_path).convert('RGB')
        self.original_width, self.original_height = self.img_pil.size
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def resize_image(self, scale):
        self.scale = scale
        new_width = int(self.original_width * self.scale)
        new_height = int(self.original_height * self.scale)
        resized_img = self.img_pil.resize((new_width, new_height), Image.NEAREST) 
        return resized_img, new_width, new_height

    def get_original_image(self):
        return self.img_pil

    def update_offsets(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
