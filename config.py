from PIL import Image

class Config:
    image_path = "C:\\Users\\micha\\Pictures\\Davide_Brocchi_2021-01-17 21_45_21-Window.jpg"  # Replace with your actual path
    ZOOM_FACTOR = 0.1
    MAX_ZOOM_LEVEL = 25  # Set an appropriate maximum zoom level
    DEBUG = True # Set to False to disable debug prints
    ANTIALIASING = Image.NEAREST #Image.Resampling.LANCZOS
    USE_CACHE = True  # Flag to enable or disable caching
    THUMBNAIL_SIZE = 32
    image_formats_list = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')