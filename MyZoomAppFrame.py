import wx
import wx.lib.inspection
from PIL import Image

class MyZoomAppFrame(wx.Frame):
    image_display_portion = None


    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        
        self.panel = wx.Panel(self)

        # Open the image and convert it to RGB format
        self.image_path = "C:\\Users\\micha\\Pictures\\Davide_Brocchi_2021-01-17 21_45_21-Window.jpg"  # Replace with your actual path
        self.img_pil = Image.open(self.image_path).convert('RGB')

        # Store the original image size
        self.original_width, self.original_height = self.img_pil.size

        # Convert PIL Image to wx.Image
        self.img_wx = wx.Image(self.original_width, self.original_height)
        self.img_wx.SetData(self.img_pil.convert("RGB").tobytes())

        # Create a wx.Bitmap from the wx.Image
        self.bitmap = wx.Bitmap(self.img_wx)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.static_bitmap = wx.GenericStaticBitmap(self.panel, -1, self.bitmap, wx.Point(1,1)) # wx.Point(1000,100))
        image_display_portion = self.static_bitmap
        sizer.Add(self.static_bitmap, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)

        self.scale = 1.0
        self.zooming = False
        self.offset_x = 0
        self.offset_y = 0

        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_MOTION, self.on_motion)
        self.static_bitmap.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.static_bitmap.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.static_bitmap.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.static_bitmap.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.static_bitmap.Bind(wx.EVT_MOTION, self.on_drag)

        # Set focus to the panel to capture key events
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()

    # Handle left Mouse Button Action
    def on_left_down(self, event):
        print("Left Mouse down")
        self.zoom_in(event)
        self.zooming = True

    def on_left_up(self, event):
        print("Left Mouse up")
        self.zooming = False

    # Handle right Mouse Button Action
    def on_right_down(self, event):
        print("Right Mouse down")
        self.zoom_out(event)
        self.zooming = True

    def on_right_up(self, event):
        print("Right Mouse up")
        self.zooming = False

    def zoom_in(self, event):
        zoom_factor = 1.1
        self.animate_zoom(zoom_factor, event.GetPosition())

    def zoom_out(self, event):
        zoom_factor = 0.9
        self.animate_zoom(zoom_factor, event.GetPosition())

    def animate_zoom(self, factor, mouse_pos):
        old_scale = self.scale
        self.scale *= factor
        new_width = int(self.original_width * self.scale)
        new_height = int(self.original_height * self.scale)

        # Calculate the new offset to center the zoom around the mouse position
        mouse_x, mouse_y = mouse_pos
        self.offset_x = (mouse_x + self.offset_x) * factor - mouse_x
        self.offset_y = (mouse_y + self.offset_y) * factor - mouse_y

        resized_img = self.img_pil.resize((new_width, new_height), None) #Image.Resampling.LANCZOS
        self.img_wx = wx.Image(new_width, new_height)
        self.img_wx.SetData(resized_img.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(self.img_wx)

        self.static_bitmap.SetBitmap(self.bitmap)
        self.panel.Refresh()
        print(f"Zoomed to scale: {self.scale}, New dimensions: {new_width}x{new_height}, Offset: ({self.offset_x}, {self.offset_y})")

    def reset_zoom(self):
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.img_wx = wx.Image(self.original_width, self.original_height)
        self.img_wx.SetData(self.img_pil.convert("RGB").tobytes())
        self.bitmap = wx.Bitmap(self.img_wx)
        #self.static_bitmap.SetBitmap(self.bitmap)
        self.panel.Refresh()
        print("Zoom reset to original dimensions.")

    def on_paint(self, event):
        #dc = wx.PaintDC(self.panel)
        #dc.DrawBitmap(self.bitmap, 100, 200)  #self.offset_x*(-1), self.offset_y*(-1))
        self.panel.Refresh()


    def on_motion(self, event):
        if not self.zooming:
            return
        self.zoom_in(event)

    def on_drag(self, event):
        if not event.Dragging():
            event.Skip()
            return
        event.Skip()
        print("Dragging position", event.GetPosition())

    def on_key(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ADD or keycode == wx.WXK_NUMPAD_ADD:  # '+' key
            print("Plus key pressed")
            self.animate_zoom(1.1, self.panel.ScreenToClient(wx.GetMousePosition()))  # Zoom in
        elif keycode == wx.WXK_SUBTRACT or keycode == wx.WXK_NUMPAD_SUBTRACT:  # '-' key
            print("Minus key pressed")
            self.animate_zoom(0.9, self.panel.ScreenToClient(wx.GetMousePosition()))  # Zoom out
        elif keycode == ord('0') or keycode == wx.WXK_NUMPAD0:  # '0' key
            print("0 key pressed")
            self.reset_zoom()  # Reset zoom
        else:
            event.Skip()
