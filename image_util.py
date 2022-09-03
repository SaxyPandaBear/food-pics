from PIL import Image
from tempfile import TemporaryFile
import requests


def compute_image_hash(img_url: str) -> int:
    """
    Download an image file from the given url, open it, and
    return the hash of the image. This uses a temporary file
    to prevent cluttering disk space with image files.
    """
    print(f"Downloading image from {img_url}")
    with TemporaryFile() as f:
        bytes = requests.get(img_url).content
        f.write(bytes)

        # don't need to close the file after writing (hopefully),
        # so just read from here, and then compute the hash.
        with Image.open(f) as im:
            print("Calculating image hash")
            return hash(im.tobytes())
