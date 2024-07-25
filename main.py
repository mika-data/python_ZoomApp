import wx
import wx.lib.inspection
from PIL import Image
from MyZoomAppControllerFrame import MyZoomAppControllerFrame
from MyZoomAppFrame import MyZoomAppFrame




def main():
    app = wx.App()

    frame = MyZoomAppFrame(None, -1, title = 'Zoom into Images')
    frame.Show()
    frameController = MyZoomAppControllerFrame(frame, -1 , title = "ZoomController")
    frameController.Show()
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
