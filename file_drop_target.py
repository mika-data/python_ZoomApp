import wx
from PIL import Image

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filepath in filenames:
            try:
                img = Image.open(filepath)
                self.window.load_image(filepath)
            except Exception as e:
                wx.MessageBox(f"Unable to open file {filepath}: {e}", "Error", wx.ICON_ERROR)
        return True
