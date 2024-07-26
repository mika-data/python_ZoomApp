import wx

class BirdsEyeView(wx.Frame):
    def __init__(self, parent, id, title, controller):
        super().__init__(parent, id, title)
        self.controller = controller
        self.panel = wx.Panel(self)
        self.init_ui()
        self.bind_events()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(sizer)

    def bind_events(self):
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_SIZE, self.on_size)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def update_image(self):
        print("update_image called from birds_eye_view")
        frame_width, frame_height = self.panel.GetSize()
        model = self.controller.model
        aspect_ratio = model.original_width / model.original_height

        if frame_width / frame_height > aspect_ratio:
            self.resized_height = frame_height
            self.resized_width = int(frame_height * aspect_ratio)
        else:
            self.resized_width = frame_width
            self.resized_height = int(frame_width / aspect_ratio)

        self.resized_img = model.img_pil.resize((self.resized_width, self.resized_height), None) # Image.Resampling.LANCZOS
        img_wx = wx.Image(self.resized_width, self.resized_height)
        img_wx.SetData(self.resized_img.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(img_wx)

    def refresh(self):
        print("refresh called from birds_eye_view")
        self.panel.Refresh()

    def on_paint(self, event):
        print("on_paint called from birds_eye_view")
        dc = wx.PaintDC(self.panel)
        upper_left_x = 0
        upper_left_y = 0
        print(f"Birds-eye View: Drawing bitmap at ({upper_left_x}, {upper_left_y})")
        dc.DrawBitmap(self.bitmap, 0, 0, True)
        model = self.controller.model
        zoom_rect_width = self.resized_width * self.GetSize().GetWidth() / model.original_width / model.scale
        zoom_rect_height = self.resized_height * self.GetSize().GetHeight() / model.original_height / model.scale
        zoom_rect_x = self.resized_width * model.offset_x / model.original_width / model.scale
        zoom_rect_y = self.resized_height * model.offset_y / model.original_height / model.scale

        dc.SetBrush(wx.Brush("green", wx.TRANSPARENT))
        dc.SetPen(wx.Pen(wx.Colour(0, 255, 0), 2))
        dc.DrawRectangle(zoom_rect_x, zoom_rect_y, zoom_rect_width, zoom_rect_height)

    def on_size(self, event):
        print("on_size called from birds_eye_view")
        self.update_image()
        self.panel.Refresh()
        event.Skip()

    def on_left_down(self, event):
        mouse_x, mouse_y = event.GetPosition()
        model = self.controller.model
        new_offset_x = (mouse_x / self.resized_width * model.original_width * model.scale) - (self.GetSize().GetWidth() // 2)
        new_offset_y = (mouse_y / self.resized_height * model.original_height * model.scale) - (self.GetSize().GetHeight() // 2)
        self.controller.update_view(new_offset_x, new_offset_y)
        self.panel.Refresh()

    def on_close(self, event):
        try:
            self.controller.zoom_view.Close()
        except wx._core.wxAssertionError:
            pass
        except Exception as e:
            pass
        self.Destroy()
