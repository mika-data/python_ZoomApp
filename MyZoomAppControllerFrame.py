import wx

class MyZoomAppControllerFrame(wx.Frame):
        
    def __init__(self, parent, id, title):

        wx.Frame.__init__(self, parent, id, title)
        
        self.panel = wx.Panel(self)