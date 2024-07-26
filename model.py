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
        self.cache = {}  # Initialize cache
        self.full_resized_img = None

    def resize_image(self, scale):
        if Config.use_cache:
            if scale in self.cache:
                return self.cache[scale]  # Return cached image if available

            self.scale = scale
            new_width = int(self.original_width * self.scale)
            new_height = int(self.original_height * self.scale)
            resized_img = self.img_pil.resize((new_width, new_height), Config.ANTIALIASING)  # Use Config.ANTIALIASING for resampling
            self.cache[scale] = (resized_img, new_width, new_height)  # Cache the resized image
            return resized_img, new_width, new_height
        else:
            self.scale = scale
            new_width = int(self.original_width * self.scale)
            new_height = int(self.original_height * self.scale)
            self.full_resized_img = self.img_pil.resize((new_width, new_height), Config.ANTIALIASING)  # Resize the entire image
            return self.full_resized_img, new_width, new_height

    def get_cached_image(self, scale, offset_x, offset_y, width, height):
        """
        Get a portion of the cached image.
        """
        resized_img, _, _ = self.resize_image(scale)
        box = (int(offset_x), int(offset_y), int(offset_x + width), int(offset_y + height))
        cropped_img = resized_img.crop(box)
        return cropped_img

    def get_original_image(self):
        return self.img_pil

    def update_offsets(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
        
    def get_full_resized_image(self):
        return self.full_resized_img