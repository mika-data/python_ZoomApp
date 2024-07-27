import wx
import threading
import time
import random
import numpy as np
from config import Config
from zoom_event_controller import ZoomEventController

class DebugView(wx.Frame):
    def __init__(self, parent, id, title, controller):
        super().__init__(parent, id, title)
        self.controller = controller
        self.panel = wx.Panel(self)
        self.bitmap = None
        self.hover_block = None
        self.status_bar = self.CreateStatusBar()
        self.init_ui()
        self.event_controller = ZoomEventController(self, controller)

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(sizer)
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()

    def update_image(self, img):
        if Config.DEBUG:
            print("update_image called from debug_view")
        img_wx = wx.Image(img.size[0], img.size[1])
        img_wx.SetData(img.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(img_wx)
        self.refresh()

    def refresh(self):
        if Config.DEBUG:
            print("refresh called from debug_view")
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

        if Config.DEBUG:
            print(f"Hover Block Position: ({x_block}, {y_block}) with block size ({block_w}, {block_h})")
            print(f"Mouse Position: ({x}, {y}), Adjusted Position: ({adjusted_x}, {adjusted_y}), "\
                  +f"Offsets: ({ox:.2f}, {oy:.2f}), Scale: {s:.2f}")

        # Set the hover block with the calculated dimensions
        self.hover_block = (x_block, y_block, block_w, block_h)

    def on_paint(self, event):
        if Config.DEBUG:
            print("on_paint called from debug_view")
        dc = wx.PaintDC(self.panel)
        dc.Clear()
        model = self.controller.model
        upper_left_x = -model.offset_x
        upper_left_y = -model.offset_y
        if Config.DEBUG:
            print(f"Debug View: Drawing bitmap at ({upper_left_x}, {upper_left_y})")
        if self.bitmap:
            dc.DrawBitmap(self.bitmap, upper_left_x, upper_left_y)

        # Draw the pink dashed line around the pixel block if hovering
        if self.hover_block:
            x, y, block_w, block_h = self.hover_block
            dc.SetPen(wx.Pen(wx.Colour(255, 20, 147), 1, wx.PENSTYLE_SHORT_DASH))  # Pink dashed line
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(x, y, block_w, block_h)

            if Config.DEBUG:
                print(f"Drawing hover block at: ({x}, {y}) with size ({block_w}, {block_h})")

    def bind_events(self):
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_MOTION, self.on_motion)

    def on_motion(self, event):
        if not self.event_controller.zooming:
            x, y = event.GetPosition()
            self.update_hover_block(x, y)
            self.refresh()

    def set_hover_block(self, x, y, block_w, block_h):
        self.hover_block = (x, y, block_w, block_h)
        self.update_hover_block_bitmap()
        self.panel.Refresh()

    def update_hover_block_bitmap(self):
        if self.hover_block:
            x, y, block_w, block_h = self.hover_block
            print(f"Hover block - X: {x}, Y: {y}, W: {block_w}, H: {block_h}")

            # Ensure the block is within image boundaries
            model = self.controller.model
            if x < 0 or y < 0 or x + block_w > model.img_pil.width or y + block_h > model.img_pil.height:
                print("Hover block is out of image boundaries")
                self.status_bar.SetStatusText("Block out of image boundaries")
                return

            try:
                # Crop the block from the original image
                block_img = model.img_pil.crop((x, y, x + block_w, y + block_h))
                block_np = np.array(block_img)
                print(f"Block numpy array shape: {block_np.shape}")

                if block_np.size == 0:
                    print(f"Invalid block size, array is empty for block ({x}, {y}) with size ({block_w}, {block_h})")
                    avg_color = [0, 0, 0]
                else:
                    avg_color = block_np.mean(axis=(0, 1))
                    if not np.isfinite(avg_color).all():
                        print(f"Invalid color values found for block ({x}, {y}) with size ({block_w}, {block_h})")
                        avg_color = [0, 0, 0]

                self.status_bar.SetStatusText(f"Size: {block_w}x{block_h}, Color: {avg_color}")
                
                # Create wx.Bitmap from the block image
                img_wx = wx.Image(block_img.size[0], block_img.size[1])
                img_wx.SetData(block_img.convert("RGB").tobytes())
                self.bitmap = wx.Bitmap(img_wx)

            except Exception as e:
                print(f"Error processing hover block: {e}")
                self.status_bar.SetStatusText(f"Error: {e}")
