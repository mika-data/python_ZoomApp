from PIL import Image
from config import Config
import time
import numpy as np
from thumbnail_generator import ThumbnailGenerator
import os

class ZoomController:
    def __init__(self, model, zoom_view, birds_eye_view, debug_view=None):
        self.model = model
        self.zoom_view = zoom_view
        self.birds_eye_view = birds_eye_view
        self.debug_view = debug_view

    def zoom_in(self, mouse_pos):
        if self.model.scale < Config.MAX_ZOOM_LEVEL:
            self._animate_zoom(1 + Config.zoom_factor, mouse_pos)
        else:
            self.find_best_match()

    def zoom_out(self, mouse_pos):
        self._animate_zoom(1 - Config.zoom_factor, mouse_pos)

    def reset_zoom(self):
        self.model.scale = 1.0
        self.model.offset_x = 0
        self.model.offset_y = 0
        self.zoom_view.update_image(self.model.get_original_image())
        self.birds_eye_view.update_image()
        if self.debug_view:
            self.debug_view.update_image()

    def _animate_zoom(self, factor, mouse_pos):
        start_time = time.time()  # Start measuring time

        old_scale = self.model.scale
        new_scale = old_scale * factor
        if new_scale > Config.MAX_ZOOM_LEVEL:
            new_scale = Config.MAX_ZOOM_LEVEL

        mouse_x, mouse_y = mouse_pos
        offset_x = (mouse_x + self.model.offset_x) * factor - mouse_x
        offset_y = (mouse_y + self.model.offset_y) * factor - mouse_y
        resized_img, new_width, new_height = self.model.resize_image(new_scale)
        self.model.update_offsets(offset_x, offset_y)

        # Use the cached portion of the image
        w = self.zoom_view.GetSize().GetWidth()
        h = self.zoom_view.GetSize().GetHeight()
        if Config.use_cache:
            cropped_img = self.model.get_cached_image(new_scale, offset_x, offset_y, w, h)
        else:
            cropped_img = resized_img.crop((int(offset_x), int(offset_y), int(offset_x + w), int(offset_y + h)))
        self.zoom_view.update_image(cropped_img)
        self.birds_eye_view.update_image()
        if self.debug_view:
            self.debug_view.update_image()
        self.zoom_view.refresh()
        self.birds_eye_view.refresh()

        end_time = time.time()  # Stop measuring time
        elapsed_time = end_time - start_time
        if Config.DEBUG:
            print(f"Zoom level: {new_scale}, Time taken: {elapsed_time:.4f} seconds")

    def update_view(self, offset_x, offset_y):
        if Config.DEBUG:
            print("update_view called in ZoomController")
        if self.model.offset_x != offset_x or self.model.offset_y != offset_y:
            self.model.update_offsets(offset_x, offset_y)
            self.zoom_view.refresh()
            self.birds_eye_view.refresh()
            if self.debug_view:
                self.debug_view.update_image()

    def load_image(self, image_path):
        self.model.image_path = image_path  # Update the image path in the model
        self.model.img_pil = Image.open(image_path).convert('RGB')
        self.model.original_width, self.model.original_height = self.model.img_pil.size
        self.model.cache.clear()  # Clear the cache when loading a new image
        ThumbnailGenerator.create_thumbnails(image_path)
        self.reset_zoom()

    def find_best_match(self):
        print("looking for best match")
        s = self.model.scale
        ox = self.model.offset_x
        oy = self.model.offset_y
        w = self.zoom_view.GetSize().GetWidth()
        h = self.zoom_view.GetSize().GetHeight()
        cached_img = self.model.get_cached_image(s, ox, oy, w, h)
        cached_img_avg_color = np.array(cached_img).mean(axis=(0, 1))
        print(f"Cached image average color: {cached_img_avg_color[:5]}")

        thumbnail_avg_colors = ThumbnailGenerator.get_thumbnail_average_colors(os.path.dirname(self.model.image_path))
        if not thumbnail_avg_colors:
            print("No thumbnails found.")
            return

        print("Thumbnail average colors (first 5):")
        for i, (thumb_name, thumb_avg_color) in enumerate(thumbnail_avg_colors.items()):
            print(f"{thumb_name}: {thumb_avg_color}")
            if i >= 4:
                break

        best_match = None
        min_distance = float('inf')

        for thumb_name, thumb_avg_color in thumbnail_avg_colors.items():
            distance = np.linalg.norm(cached_img_avg_color - thumb_avg_color)
            if Config.DEBUG:
                print(f"Comparing with {thumb_name}, distance: {distance}")
            if distance < min_distance:
                min_distance = distance
                best_match = thumb_name

        if best_match:
            print(f"Best match: {best_match} with color distance: {min_distance}")
