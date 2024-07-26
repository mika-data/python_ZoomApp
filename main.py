import wx
import wx.lib.inspection
from config import Config
from model import ImageModel
from zoom_controller import ZoomController
from zoom_view import ZoomView
from birds_eye_view import BirdsEyeView

def main():
    app = wx.App()
    config = Config()
    model = ImageModel(config.image_path)
    
    zoom_view = ZoomView(None, -1, 'Zoomed Image Frame', None)
    birds_eye_view = BirdsEyeView(None, -1, 'Birds-eye View Frame', None)
    
    controller = ZoomController(model, zoom_view, birds_eye_view)
    zoom_view.controller = controller
    birds_eye_view.controller = controller
    
    zoom_view.Show()
    birds_eye_view.Show()

    # Display the initial image before zooming
    zoom_view.update_image(zoom_view.controller.model.get_original_image())  
    birds_eye_view.update_image()
    
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
