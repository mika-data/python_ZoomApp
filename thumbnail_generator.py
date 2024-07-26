import os
from PIL import Image
from config import Config
import numpy as np

class ThumbnailGenerator:
    

    @staticmethod
    def create_thumbnails(image_path):
        size = Config.THUMBNAIL_SIZE
        directory = os.path.dirname(image_path)
        thumb_dir = os.path.join(directory, "_thumbs" + str(size) + "x" + str(size))

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

    @staticmethod
    def calculate_average_color(image_path):
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            np_img = np.array(img)
            w, h, _ = np_img.shape
            return np_img.reshape((w * h, 3)).mean(axis=0)

    @staticmethod
    def get_thumbnail_average_colors(thumb_dir):
        avg_colors = {}
        if not os.path.exists(thumb_dir):
            return avg_colors

        for thumb_name in os.listdir(thumb_dir):
            thumb_path = os.path.join(thumb_dir, thumb_name)
            thumb_img = Image.open(thumb_path)
            thumb_np = np.array(thumb_img)
            thumb_avg_color = thumb_np.mean(axis=(0, 1))
            avg_colors[thumb_name] = thumb_avg_color

        return avg_colors

    @staticmethod
    def find_best_match_thumbnail(avg_color, thumb_dir):
        min_distance = float('inf')
        best_match = None
        if not os.path.exists(thumb_dir):
            return None

        for thumb_name in os.listdir(thumb_dir):
            thumb_path = os.path.join(thumb_dir, thumb_name)
            thumb_img = Image.open(thumb_path)
            thumb_np = np.array(thumb_img)
            thumb_avg_color = thumb_np.mean(axis=(0, 1))
            distance = np.linalg.norm(avg_color - thumb_avg_color)
            if distance < min_distance:
                min_distance = distance
                best_match = thumb_path

        return best_match
