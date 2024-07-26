import wx
from config import Config
from PIL import Image
import os
import numpy as np

class DebugView(wx.Frame):
    def __init__(self, parent, id, title, model):
        super().__init__(parent, id, title)
        self.panel = wx.Panel(self)
        self.bitmap = None
        self.hover_block = None
        self.model = model
        self.init_ui()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(sizer)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)

    def refresh(self):
        if Config.DEBUG:
            print("refresh called from debug_view")
        self.panel.Refresh()

    def set_hover_block(self, x, y, block_w, block_h):
        self.hover_block = (x, y, block_w, block_h)
        self.update_hover_block_bitmap()
        self.panel.Refresh()

    def update_hover_block_bitmap(self):
        if self.hover_block:
            x, y, block_w, block_h = self.hover_block
            # Crop the block from the original image
            block_img = self.model.img_pil.crop((x, y, x + block_w, y + block_h))
            img_wx = wx.Image(block_img.size[0], block_img.size[1])
            img_wx.SetData(block_img.convert("RGB").tobytes())
            self.bitmap = wx.Bitmap(img_wx)

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.Clear()
        panel_w, panel_h = self.panel.GetSize()

        if self.bitmap:
            # Calculate the position to center the bitmap on the panel
            bitmap_w, bitmap_h = self.bitmap.GetSize()
            x_pos = (panel_w - bitmap_w) // 2
            y_pos = (panel_h - bitmap_h) // 2
            dc.DrawBitmap(self.bitmap, x_pos, y_pos)

            # If the pixel block size is larger than the thumbnail size, draw the best match thumbnail
            if self.hover_block:
                x, y, block_w, block_h = self.hover_block
                if block_w > Config.THUMBNAIL_SIZE or block_h > Config.THUMBNAIL_SIZE:
                    thumb_path = self.get_best_match_thumb(x, y, block_w, block_h)
                    if thumb_path:
                        thumb_img = Image.open(thumb_path).resize((block_w, block_h))
                        thumb_wx = wx.Image(thumb_img.size[0], thumb_img.size[1])
                        thumb_wx.SetData(thumb_img.convert("RGB").tobytes())
                        thumb_bitmap = wx.Bitmap(thumb_wx)

                        # Draw the thumbnail next to the block image
                        thumb_x_pos = x_pos + bitmap_w + 10  # 10 pixels gap
                        dc.DrawBitmap(thumb_bitmap, thumb_x_pos, y_pos)

    def get_best_match_thumb(self, x, y, block_w, block_h):
        # Calculate the average color of the pixel block
        block_img = self.model.img_pil.crop((x, y, x + block_w, y + block_h))
        block_np = np.array(block_img)
        avg_color = block_np.mean(axis=(0, 1))

        # Find the best match thumbnail based on the average color
        min_distance = float('inf')
        best_match = None
        thumb_dir = os.path.join(os.path.dirname(self.model.image_path), f"_thumbs{Config.THUMBNAIL_SIZE}x{Config.THUMBNAIL_SIZE}")
        if not os.path.exists(thumb_dir):
            return None

        for thumb_name in os.listdir(thumb_dir):
            thumb_path = os.path.join(thumb_dir, thumb_name)
            thumb_img = Image.open(thumb_path)
            thumb_np = np.array(thumb_img)
            thumb_avg_color = thumb_np.mean(axis=(0, 1))
            distance = np.linalg.norm(avg_color - thumb_avg_color)
            if distance < min_distance:
                min_distance = distance
                best_match = thumb_path

        return best_match
