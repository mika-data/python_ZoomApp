import wx
import wx.lib.inspection
from config import Config
from model import ImageModel
from zoom_controller import ZoomController
from zoom_view import ZoomView
from birds_eye_view import BirdsEyeView
from debug_view import DebugView

def main():
    app = wx.App()
    config = Config()
    model = ImageModel(config.image_path)
    
    zoom_view = ZoomView(None, -1, 'Zoomed Image Frame', None)
    birds_eye_view = BirdsEyeView(None, -1, 'Birds-eye View Frame', None)
    
    debug_view = None
    if Config.DEBUG:
        debug_view = DebugView(None, -1, 'Debug View Frame', model)
    
    controller = ZoomController(model, zoom_view, birds_eye_view, debug_view)
    zoom_view.controller = controller
    birds_eye_view.controller = controller
    
    zoom_view.Show()
    birds_eye_view.Show()
    if debug_view:
        debug_view.controller = controller  # Ensure the controller is set correctly
        debug_view.Show()

    # Display the initial image before zooming
    model.resize_image(1.0)  # Ensure the full resized image is available
    zoom_view.update_image(model.get_original_image())  
    birds_eye_view.update_image()

    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()