import wx
import os
from config import Config


class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filepath in filenames:
            if os.path.isfile(filepath):
                # Check if the file is from a _thumb* directory
                if os.path.basename(os.path.dirname(filepath)).startswith('_thumb'):
                    original_file = os.path.join(os.path.dirname(os.path.dirname(filepath)), os.path.basename(filepath))
                    if os.path.exists(original_file):
                        self.window.controller.load_image(original_file)
                    else:
                        if Config.DEBUG:
                            print(f"Original file {original_file} not found.")
                else:
                    self.window.controller.load_image(filepath)
            elif os.path.isdir(filepath):
                for root, _, files in os.walk(filepath):
                    for name in files:
                        file_path = os.path.join(root, name)
                        if os.path.isfile(file_path):
                            self.window.controller.load_image(file_path)
        return True
