import wx

class ZoomView(wx.Frame):
    def __init__(self, parent, id, title, controller):
        super().__init__(parent, id, title)
        self.controller = controller
        self.panel = wx.Panel(self)
        self.static_bitmap = None
        self.zooming = False
        self.init_ui()
        self.bind_events()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.static_bitmap = wx.StaticBitmap(self.panel, -1)
        sizer.Add(self.static_bitmap, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()

    def bind_events(self):
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_MOTION, self.on_motion)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.static_bitmap.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.static_bitmap.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.static_bitmap.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.static_bitmap.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.static_bitmap.Bind(wx.EVT_MOTION, self.on_drag)

    def update_image(self, img):
        print("update_image called from zoom_view")
        img_wx = wx.Image(img.size[0], img.size[1])
        img_wx.SetData(img.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(img_wx)
        self.refresh()

    def refresh(self):
        print("refresh called from zoom_view")
        self.static_bitmap.SetBitmap(self.bitmap)
        self.panel.Refresh()

    def on_paint(self, event):
        print("on_paint called from zoom_view")
        dc = wx.PaintDC(self.panel)
        dc.Clear()
        #debug double rendering
        upper_left_x = -model.offset_x
        upper_left_y = -model.offset_y
        print(f"Zoom View: on_paint method drawing bitmap at ({upper_left_x}, {upper_left_y})")
        model = self.controller.model
        dc.DrawBitmap(self.bitmap, -model.offset_x, -model.offset_y)

    def on_motion(self, event):
        print("on_motion called from birds_eye_view")
        if not self.zooming:
            return
        self.controller.zoom_in(event.GetPosition())

    def on_drag(self, event):
        if not event.Dragging():
            event.Skip()
            return
        event.Skip()

    def on_key(self, event):
        keycode = event.GetKeyCode()
        if keycode in [wx.WXK_ADD, wx.WXK_NUMPAD_ADD]:
            self.controller.zoom_in(self.panel.ScreenToClient(wx.GetMousePosition()))
        elif keycode in [wx.WXK_SUBTRACT, wx.WXK_NUMPAD_SUBTRACT]:
            self.controller.zoom_out(self.panel.ScreenToClient(wx.GetMousePosition()))
        elif keycode in [ord('0'), wx.WXK_NUMPAD0]:
            self.controller.reset_zoom()
        else:
            event.Skip()

    def on_left_down(self, event):
        self.zooming = True
        self.controller.zoom_in(event.GetPosition())

    def on_left_up(self, event):
        self.zooming = False

    def on_right_down(self, event):
        self.zooming = True
        self.controller.zoom_out(event.GetPosition())

    def on_right_up(self, event):
        self.zooming = False
