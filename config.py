from PIL import Image

class Config:
    image_path = "C:\\Users\\micha\\Pictures\\Davide_Brocchi_2021-01-17 21_45_21-Window.jpg"  # Replace with your actual path
    zoom_factor = 0.1
    DEBUG = False # Set to False to disable debug prints
    ANTIALIASING = Image.NEAREST #Image.Resampling.LANCZOS
    use_cache = True  # Flag to enable or disable caching
