import wx
from config import Config

class DebugView(wx.Frame):
    def __init__(self, parent, id, title, model):
        super().__init__(parent, id, title)
        self.model = model
        self.panel = wx.Panel(self)
        self.bitmap = None
        self.init_ui()
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(sizer)
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()

    def update_image(self):
        img = self.model.get_full_resized_image()
        if img:
            if Config.DEBUG:
                print(f"Debug view: image of size {img.size[0]}x{img.size[1]} calculated")
            img_wx = wx.Image(img.size[0], img.size[1])
            img_wx.SetData(img.convert("RGB").tobytes())
            self.bitmap = wx.Bitmap(img_wx)
            self.panel.Refresh()
        else:
            if Config.DEBUG:
                print(f"Debug view img is None")

    def on_paint(self, event):
        self.update_image()
        if Config.DEBUG:
            print("on_paint called from debug_view")
        dc = wx.PaintDC(self)
        dc.Clear()
        if self.bitmap:
            if Config.DEBUG:
                print("DebugView.on_paint: drawing bitmap")
            dc.DrawBitmap(self.bitmap, 0, 0)
