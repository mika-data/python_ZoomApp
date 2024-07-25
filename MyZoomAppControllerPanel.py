import wx

class MyZoomAppControllerPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def OnPaint(self, event):
        print('Controller OnPaint')
        dc = wx.PaintDC(self)
       
        dc.SetPen(wx.Pen("green"))
        dc.DrawLine(10, 10, 50, 50)