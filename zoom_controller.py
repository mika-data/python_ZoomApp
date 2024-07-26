from PIL import Image
from config import Config
import time
from thumbnail_generator import ThumbnailGenerator

class ZoomController:
    def __init__(self, model, zoom_view, birds_eye_view, debug_view=None):
        self.model = model
        self.zoom_view = zoom_view
        self.birds_eye_view = birds_eye_view
        self.debug_view = debug_view

    def zoom_in(self, mouse_pos):
        if self.model.scale < Config.MAX_ZOOM_LEVEL:
            self._animate_zoom(1 + Config.zoom_factor, mouse_pos)

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
        if Config.use_cache:
            cropped_img = self.model.get_cached_image(new_scale, offset_x, offset_y, self.zoom_view.GetSize().GetWidth(), self.zoom_view.GetSize().GetHeight())
        else:
            cropped_img = resized_img.crop((int(offset_x), int(offset_y), int(offset_x + self.zoom_view.GetSize().GetWidth()), int(offset_y + self.zoom_view.GetSize().GetHeight())))
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
        self.model.img_pil = Image.open(image_path).convert('RGB')
        self.model.original_width, self.model.original_height = self.model.img_pil.size
        self.model.cache.clear()  # Clear the cache when loading a new image
        ThumbnailGenerator.create_thumbnails(image_path)
        self.reset_zoom()
