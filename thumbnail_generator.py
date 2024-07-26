import os
from PIL import Image
from config import Config

class ThumbnailGenerator:
    @staticmethod
    def create_thumbnails(image_path):
        size = Config.THUMBNAIL_SIZE
        directory = os.path.dirname(image_path)
        thumb_dir = os.path.join(directory, f"_thumbs{size}x{size}")

        if not os.path.exists(thumb_dir):
            os.makedirs(thumb_dir)

        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                file_path = os.path.join(directory, filename)
                thumb_path = os.path.join(thumb_dir, filename)
                
                if not os.path.exists(thumb_path):
                    with Image.open(file_path) as img:
                        img.thumbnail((size, size), Config.ANTIALIASING)
                        img.save(thumb_path)
                        if Config.DEBUG:
                            print(f"Thumbnail created for {filename} at {thumb_path}")
