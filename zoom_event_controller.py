import wx
import threading
import time
import random
from config import Config

class ZoomEventController:
    def __init__(self, zoom_view, controller):
        self.zoom_view = zoom_view
        self.controller = controller
        self.zooming = False
        self.automatic_mode = False
        self.bind_events()

    def bind_events(self):
        self.zoom_view.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.zoom_view.panel.Bind(wx.EVT_MOTION, self.on_motion)
        self.zoom_view.panel.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.zoom_view.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.zoom_view.panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.zoom_view.panel.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.zoom_view.panel.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        # self.zoom_view.panel.Bind(wx.EVT_MOTION, self.on_drag)

    def on_paint(self, event):
        if Config.DEBUG:
            print("on_paint called from zoom_view")
        dc = wx.PaintDC(self.zoom_view.panel)
        dc.Clear()
        if Config.USE_CACHE:
            upper_left_x = 0
            upper_left_y = 0
        else:
            model = self.zoom_view.controller.model
            upper_left_x = -model.offset_x
            upper_left_y = -model.offset_y
        if Config.DEBUG:
            print(f"Zoom View: Drawing bitmap at ({upper_left_x}, {upper_left_y})")
        if self.zoom_view.bitmap:
            dc.DrawBitmap(self.zoom_view.bitmap, upper_left_x, upper_left_y)

        # Draw the pink dashed line around the pixel block if hovering
        if self.zoom_view.hover_block:
            x, y, block_w, block_h = self.zoom_view.hover_block
            dc.SetPen(wx.Pen(wx.Colour(255, 20, 147), 1, wx.PENSTYLE_SHORT_DASH))  # Pink dashed line
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(x, y, block_w, block_h)

    def on_motion(self, event):
        if not self.zooming:
            x, y = event.GetPosition()
            self.zoom_view.update_hover_block(x, y)
            self.zoom_view.panel.Refresh()
        else:
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
        elif keycode in [ord('A'), ord('a')]:
            self.toggle_automatic_mode()
        elif keycode == wx.WXK_ESCAPE:
            self.automatic_mode = False
        else:
            event.Skip()

    def toggle_automatic_mode(self):
        self.automatic_mode = not self.automatic_mode
        if self.automatic_mode:
            threading.Thread(target=self.run_automatic_zoom).start()

    def run_automatic_zoom(self):
        while self.automatic_mode:
            wx.CallAfter(self.automatic_zoom_step)
            time.sleep(0.2)

    def automatic_zoom_step(self):
        if not self.automatic_mode:
            return
        w, h = self.zoom_view.GetSize().GetWidth(), self.zoom_view.GetSize().GetHeight()
        random_x = random.randint(0, w)
        random_y = random.randint(0, h)
        self.zoom_view.controller.zoom_in((random_x, random_y))

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
