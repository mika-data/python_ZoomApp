from PIL import Image

class ZoomController:
    def __init__(self, model, zoom_view, birds_eye_view):
        self.model = model
        self.zoom_view = zoom_view
        self.birds_eye_view = birds_eye_view

    def zoom_in(self, mouse_pos):
        self._animate_zoom(1.1, mouse_pos)

    def zoom_out(self, mouse_pos):
        self._animate_zoom(0.9, mouse_pos)

    def reset_zoom(self):
        self.model.scale = 1.0
        self.model.offset_x = 0
        self.model.offset_y = 0
        self.zoom_view.update_image(self.model.get_original_image())
        self.birds_eye_view.update_image()

    def _animate_zoom(self, factor, mouse_pos):
        old_scale = self.model.scale
        new_scale = old_scale * factor
        mouse_x, mouse_y = mouse_pos
        offset_x = (mouse_x + self.model.offset_x) * factor - mouse_x
        offset_y = (mouse_y + self.model.offset_y) * factor - mouse_y
        resized_img, new_width, new_height = self.model.resize_image(new_scale)
        self.model.update_offsets(offset_x, offset_y)
        self.zoom_view.update_image(resized_img)
        self.birds_eye_view.update_image()
        self.zoom_view.refresh()
        self.birds_eye_view.refresh()

    def update_view(self, offset_x, offset_y):
        print("update_view called in ZoomController")
        if self.model.offset_x != offset_x or self.model.offset_y != offset_y:
            self.model.update_offsets(offset_x, offset_y)
            self.zoom_view.refresh()
            self.birds_eye_view.refresh()

    def load_image(self, image_path):
        self.model.img_pil = Image.open(image_path).convert('RGB')
        self.model.original_width, self.model.original_height = self.model.img_pil.size
        self.reset_zoom()
