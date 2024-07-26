import wx
from config import Config
from PIL import Image
import os
import numpy as np
from thumbnail_generator import ThumbnailGenerator

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
        self.status_bar = self.CreateStatusBar()

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
            print(f"Hover block - X: {x}, Y: {y}, W: {block_w}, H: {block_h}")

                        # Ensure the block is within image boundaries
            if x < 0 or y < 0 or x + block_w > self.model.img_pil.width or y + block_h > self.model.img_pil.height:
                print("Hover block is out of image boundaries")
                self.status_bar.SetStatusText("Block out of image boundaries")
                return

            try:
                # Crop the block from the original image
                block_img = self.model.img_pil.crop((x, y, x + block_w, y + block_h))
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

        size=Config.THUMBNAIL_SIZE
        # Find the best match thumbnail based on the average color
        thumb_dir = os.path.join(os.path.dirname(self.model.image_path), f"_thumbs{size}x{size}")
        best_match = ThumbnailGenerator.find_best_match_thumbnail(avg_color, thumb_dir)
        return best_match
