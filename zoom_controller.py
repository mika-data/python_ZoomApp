from PIL import Image, ImageDraw
from config import Config
import time
import numpy as np
from thumbnail_generator import ThumbnailGenerator
import os
import random

class ZoomController:
    def __init__(self, model, zoom_view, birds_eye_view, debug_view=None):
        self.model = model
        self.zoom_view = zoom_view
        self.birds_eye_view = birds_eye_view
        self.debug_view = debug_view
        self.initial_offset_x = 0
        self.initial_offset_y = 0

    def update_initial_offset(self):
        s = self.model.scale
        self.initial_offset_x = self.model.offset_x % s
        self.initial_offset_y = self.model.offset_y % s

        if Config.DEBUG:
            print(f"Initial Offset: ({self.initial_offset_x}, {self.initial_offset_y})")

    def set_zoom_level(self, zoom_level):
        # Update the zoom level
        self.model.set_zoom_level(zoom_level)
        self.update_initial_offset()
        self.zoom_view.refresh()
        self.birds_eye_view.refresh()
        if self.debug_view:
            self.debug_view.refresh()
            
    def zoom_in(self, mouse_pos):
        if self.model.scale < Config.MAX_ZOOM_LEVEL:
            self._animate_zoom(1 + Config.ZOOM_FACTOR, mouse_pos)
        else:
            self.find_best_match()

    def zoom_out(self, mouse_pos):
        self._animate_zoom(1 - Config.ZOOM_FACTOR, mouse_pos)

    def reset_zoom(self):
        self.model.scale = 1.0
        self.model.offset_x = 0
        self.model.offset_y = 0
        self.zoom_view.update_image(self.model.get_original_image())
        self.birds_eye_view.update_image()
        if self.debug_view:
            self.debug_view.update_hover_block_bitmap()

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
        if Config.USE_CACHE:
            cropped_img = self.model.get_cached_image(new_scale, offset_x, offset_y, w, h)
        else:
            cropped_img = resized_img.crop((int(offset_x), int(offset_y), int(offset_x + w), int(offset_y + h)))
        self.zoom_view.update_image(cropped_img)
        self.birds_eye_view.update_image()
        if self.debug_view:
            self.debug_view.update_hover_block_bitmap()
        self.zoom_view.refresh()
        self.birds_eye_view.refresh()

        end_time = time.time()  # Stop measuring time
        elapsed_time = end_time - start_time
        if Config.DEBUG:
            print(f"Zoom level: {new_scale:.2f}, Time taken: {elapsed_time:.4f} seconds")

    def update_view(self, offset_x, offset_y):
        if Config.DEBUG:
            print("update_view called in ZoomController")
        if self.model.offset_x != offset_x or self.model.offset_y != offset_y:
            self.model.update_offsets(offset_x, offset_y)
            self.zoom_view.refresh()
            self.birds_eye_view.refresh()
            if self.debug_view:
                self.debug_view.update_hover_block_bitmap()

    def load_image(self, image_path):
        self.model.image_path = image_path  # Update the image path in the model
        self.model.img_pil = Image.open(image_path).convert('RGB')
        self.model.original_width, self.model.original_height = self.model.img_pil.size
        self.model.cache.clear()  # Clear the cache when loading a new image
        ThumbnailGenerator.create_thumbnails(image_path)
        self.reset_zoom()

    def find_best_match(self):
        print("looking for best match")
        scale = self.model.scale
        ox = self.model.offset_x
        oy = self.model.offset_y
        w = self.zoom_view.GetSize().GetWidth()
        h = self.zoom_view.GetSize().GetHeight()
        cached_img = self.model.get_cached_image(scale, ox, oy, w, h)
        cached_img_np = np.array(cached_img)
        print(f"Cached image size: {cached_img_np.shape}")

        # Calculate the pixel block dimensions
        original_w = self.model.original_width
        original_h = self.model.original_height
        block_w = int(original_w / w)
        block_h = int(original_h / h)
        print(f"Block dimensions: {block_w} x {block_h}")

        avg_colors = []
        for y in range(0, cached_img_np.shape[0], block_h):
            for x in range(0, cached_img_np.shape[1], block_w):
                avg_colors.append(cached_img_np[y, x])

        print(f"First 5 cached image colors: {avg_colors[:5]}")
        size = Config.THUMBNAIL_SIZE
        thumb_dir = os.path.join(os.path.dirname(self.model.image_path), f"_thumbs{size}x{size}")
        if not os.path.exists(thumb_dir):
            print("No thumbnails found.")
            return

        best_match = {}
        for y in range(0, cached_img_np.shape[0], block_h):
            for x in range(0, cached_img_np.shape[1], block_w):
                block_img = self.model.img_pil.crop((x, y, x + block_w, y + block_h))
                block_np = np.array(block_img)
                avg_color = block_np.mean(axis=(0, 1))
                best_thumbnail = ThumbnailGenerator.find_best_match_thumbnail(avg_color, thumb_dir)
                best_match[(x, y)] = best_thumbnail
                if Config.DEBUG and y == 0 and x < 5 * block_w:  # Only print first row's first 5 matches for debugging
                    print(f"Pixel block ({x}, {y}) best match: {best_thumbnail}")

        print(f"Best match: {best_match[(0, 0)]}")

        # Replace each pixel block with the best matched thumbnail
        new_img = Image.new('RGB', (original_w, original_h))
        for (x, y), thumb_path in best_match.items():
            if thumb_path:
                thumb_img = Image.open(thumb_path).resize((block_w, block_h))
                new_img.paste(thumb_img, (x, y))

        # Choose a random pixel block for debugging
        rand_x = random.randint(0, (cached_img_np.shape[1] // block_w) - 1) * block_w
        rand_y = random.randint(0, (cached_img_np.shape[0] // block_h) - 1) * block_h
        draw = ImageDraw.Draw(new_img)
        # Draw dashed pink line around the pixel block
        for i in range(rand_x, rand_x + block_w, 2):
            draw.line([(i, rand_y), (i + 1, rand_y)], fill="pink")
            draw.line([(i, rand_y + block_h - 1), (i + 1, rand_y + block_h - 1)], fill="pink")
        for i in range(rand_y, rand_y + block_h, 2):
            draw.line([(rand_x, i), (rand_x, i + 1)], fill="pink")
            draw.line([(rand_x + block_w - 1, i), (rand_x + block_w - 1, i + 1)], fill="pink")

        # Use the newly created image as the full-scale image
        self.model.img_pil = new_img
        self.model.original_width, self.model.original_height = new_img.size
        self.reset_zoom()  # Reset the zoom level to 0 and update views
