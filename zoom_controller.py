class ZoomController:
    def __init__(self, model, zoom_view, controller_view):
        self.model = model
        self.zoom_view = zoom_view
        self.controller_view = controller_view

    def zoom_in(self, mouse_pos):
        self._animate_zoom(1.1, mouse_pos)

    def zoom_out(self, mouse_pos):
        self._animate_zoom(0.9, mouse_pos)

    def reset_zoom(self):
        print("reset_zoom called from zoom_controller")
        self.model.scale = 1.0
        self.model.offset_x = 0
        self.model.offset_y = 0
        self.zoom_view.update_image(self.model.get_original_image())
        self.controller_view.update_image()

    def _animate_zoom(self, factor, mouse_pos):
        print("_animate_zoom called from zoom_controller")
        old_scale = self.model.scale
        new_scale = old_scale * factor
        mouse_x, mouse_y = mouse_pos
        offset_x = (mouse_x + self.model.offset_x) * factor - mouse_x
        offset_y = (mouse_y + self.model.offset_y) * factor - mouse_y
        resized_img, new_width, new_height = self.model.resize_image(new_scale)
        self.model.update_offsets(offset_x, offset_y)
        self.zoom_view.update_image(resized_img)
        self.controller_view.update_image()
        self.zoom_view.refresh()
        self.controller_view.refresh()

    def update_view(self, offset_x, offset_y):
        print("update_view called from zoom_controller")
        self.model.update_offsets(offset_x, offset_y)
        self.zoom_view.refresh()
