import wx
from file_drop_target import FileDropTarget
from config import Config
from zoom_event_controller import ZoomEventController

class ZoomView(wx.Frame):
    def __init__(self, parent, id, title, controller):
        super().__init__(parent, id, title)
        self.controller = controller
        self.panel = wx.Panel(self)
        self.bitmap = None
        self.hover_block = None
        self.init_ui()
        self.init_drag_and_drop()
        self.event_controller = ZoomEventController(self, controller)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(sizer)
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()

    def init_drag_and_drop(self):
        dt = FileDropTarget(self)
        self.SetDropTarget(dt)

    def update_image(self, img):
        if Config.DEBUG:
            print("update_image called from zoom_view")
        img_wx = wx.Image(img.size[0], img.size[1])
        img_wx.SetData(img.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(img_wx)
        self.refresh()

    def refresh(self):
        if Config.DEBUG:
            print("refresh called from zoom_view")
        self.panel.Refresh()

    def load_image(self, image_path):
        self.controller.load_image(image_path)

    def update_hover_block(self, x, y):
        # Determine scale and offsets
        s = self.controller.model.scale
        ox = self.controller.model.offset_x
        oy = self.controller.model.offset_y

        # Calculate the block dimensions based on the scale factor
        block_w = int(s)
        block_h = int(s)

        # Adjust the coordinates for the offsets
        adjusted_x = x + ox
        adjusted_y = y + oy

        # Find the pixel block the mouse is hovering over
        x_block = (adjusted_x // block_w) * block_w
        y_block = (adjusted_y // block_h) * block_h

        # Set the hover block with the calculated dimensions
        self.hover_block = (x_block, y_block, block_w, block_h)

        # Notify the debug view if available
        if self.controller.debug_view:
            self.controller.debug_view.set_hover_block(x_block, y_block, block_w, block_h)
