import wx
from PIL import Image

class MyZoomAppControllerFrame(wx.Frame):
    def __init__(self, parent, id, title, pos, size, zoom_frame, config):
        wx.Frame.__init__(self, parent, id, title)
        
        self.zoom_frame = zoom_frame
        self.panel = wx.Panel(self)

        # Use the image path from the configuration
        self.image_path = config.image_path
        self.img_pil = Image.open(self.image_path).convert('RGB')

        # Store the original image size
        self.original_width, self.original_height = self.img_pil.size

        # Initialize variables for the resized image
        self.resized_img = None
        self.resized_width = 0
        self.resized_height = 0

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(sizer)

        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_SIZE, self.on_size)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

    def on_size(self, event):
        self.update_image()
        self.panel.Refresh()
        event.Skip()

    def update_image(self):
        frame_width, frame_height = self.panel.GetSize()
        aspect_ratio = self.original_width / self.original_height

        if frame_width / frame_height > aspect_ratio:
            self.resized_height = frame_height
            self.resized_width = int(frame_height * aspect_ratio)
        else:
            self.resized_width = frame_width
            self.resized_height = int(frame_width / aspect_ratio)

        self.resized_img = self.img_pil.resize((self.resized_width, self.resized_height), Image.Resampling.LANCZOS)
        img_wx = wx.Image(self.resized_width, self.resized_height)
        img_wx.SetData(self.resized_img.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(img_wx)

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        if self.resized_img:
            # Draw the bitmap
            dc.DrawBitmap(self.bitmap, 0, 0, True)

            # Draw the green rectangle representing the zoomed portion
            zoom_frame = self.zoom_frame
            zoom_rect_width = self.resized_width * zoom_frame.GetSize().GetWidth() / zoom_frame.original_width / zoom_frame.scale
            zoom_rect_height = self.resized_height * zoom_frame.GetSize().GetHeight() / zoom_frame.original_height / zoom_frame.scale
            zoom_rect_x = self.resized_width * zoom_frame.offset_x / zoom_frame.original_width / zoom_frame.scale
            zoom_rect_y = self.resized_height * zoom_frame.offset_y / zoom_frame.original_height / zoom_frame.scale

            dc.SetBrush(wx.Brush(wx.Colour(0, 255, 0, 50), wx.TRANSPARENT))  # Transparent green
            dc.SetPen(wx.Pen(wx.Colour(0, 255, 0), 2))  # Green border
            dc.DrawRectangle(zoom_rect_x, zoom_rect_y, zoom_rect_width, zoom_rect_height)

    def on_left_down(self, event):
        # Center the zoom frame on the clicked position
        mouse_x, mouse_y = event.GetPosition()
        zoom_frame = self.zoom_frame
        zoom_frame.offset_x = (mouse_x / self.resized_width * zoom_frame.original_width * zoom_frame.scale) - (zoom_frame.GetSize().GetWidth() // 2)
        zoom_frame.offset_y = (mouse_y / self.resized_height * zoom_frame.original_height * zoom_frame.scale) - (zoom_frame.GetSize().GetHeight() // 2)
        zoom_frame.panel.Refresh()
        self.panel.Refresh()

    def on_close_window(self, event):
        self.zoom_frame.Destroy()
        self.Destroy()
