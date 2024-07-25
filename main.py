import wx
import wx.lib.inspection
from MyZoomAppFrame import MyZoomAppFrame
from MyZoomAppControllerFrame import MyZoomAppControllerFrame
from config import Config

def main():
    app = wx.App()
    
    config = Config()
    frame = MyZoomAppFrame(None, -1, 'Zoomed Image Frame', config)
    controller_frame = MyZoomAppControllerFrame(None, -1, 'Birds-eye View Frame',
                                                 pos=(10,10), size=(460, 300),
                                                 zoom_frame=frame, config=config)
    
    frame.Show()
    controller_frame.Show()
    
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
