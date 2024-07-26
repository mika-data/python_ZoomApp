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
        self.init_ui()
        self.init_drag_and_drop()
        self.event_controller = ZoomEventController(self, self.controller)

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
