import wx
from config import Config

class ZoomEventController:
    def __init__(self, zoom_view, controller):
        self.zoom_view = zoom_view
        self.controller = controller
        self.zooming = False
        self.bind_events()

    def bind_events(self):
        self.zoom_view.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.zoom_view.panel.Bind(wx.EVT_MOTION, self.on_motion)
        self.zoom_view.panel.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.zoom_view.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.zoom_view.panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.zoom_view.panel.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.zoom_view.panel.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.zoom_view.panel.Bind(wx.EVT_MOTION, self.on_drag)

    def on_paint(self, event):
        if Config.DEBUG:
            print("on_paint called from zoom_view")
        dc = wx.PaintDC(self.zoom_view.panel)
        dc.Clear()
        if Config.use_cache:
            upper_left_x = 0
            upper_left_y = 0
        else:
            model = self.controller.model
            upper_left_x = -model.offset_x
            upper_left_y = -model.offset_y
        if Config.DEBUG:
            print(f"Zoom View: Drawing bitmap at ({upper_left_x}, {upper_left_y})")
        if self.zoom_view.bitmap:
            dc.DrawBitmap(self.zoom_view.bitmap, upper_left_x, upper_left_y)

    def on_motion(self, event):
        if not self.zooming:
            return
        self.zoom_view.controller.zoom_in(event.GetPosition())

    def on_drag(self, event):
        if not event.Dragging():
            event.Skip()
            return
        event.Skip()

    def on_key(self, event):
        keycode = event.GetKeyCode()
        if keycode in [wx.WXK_ADD, wx.WXK_NUMPAD_ADD]:
            self.zoom_view.controller.zoom_in(self.zoom_view.panel.ScreenToClient(wx.GetMousePosition()))
        elif keycode in [wx.WXK_SUBTRACT, wx.WXK_NUMPAD_SUBTRACT]:
            self.zoom_view.controller.zoom_out(self.zoom_view.panel.ScreenToClient(wx.GetMousePosition()))
        elif keycode in [ord('0'), wx.WXK_NUMPAD0]:
            self.zoom_view.controller.reset_zoom()
        else:
            event.Skip()

    def on_left_down(self, event):
        self.zooming = True
        self.zoom_view.controller.zoom_in(event.GetPosition())

    def on_left_up(self, event):
        self.zooming = False

    def on_right_down(self, event):
        self.zooming = True
        self.zoom_view.controller.zoom_out(event.GetPosition())

    def on_right_up(self, event):
        self.zooming = False
