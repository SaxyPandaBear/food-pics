from image_util import compute_image_hash
import unittest

# Validating https://github.com/SaxyPandaBear/my-webhooks/issues/11
img1 = 'https://i.redd.it/lqiuc3pl39d81.jpg'
img2 = 'https://i.redd.it/etywihlo39d81.jpg'
img3 = 'https://i.redd.it/s7heggczlli91.jpg' # different image

class ImageUtilTest(unittest.TestCase):
    def test_calculate_hash(self):
        h1 = compute_image_hash(img1)
        h2 = compute_image_hash(img1) # check same image for consistent hash
        self.assertEqual(h1, h2)

    def test_compare_identical_images(self):
        h1 = compute_image_hash(img1)
        h2 = compute_image_hash(img2)
        self.assertEqual(h1, h2)

    def test_compare_different_images(self):
        h1 = compute_image_hash(img1)
        h2 = compute_image_hash(img3)
        self.assertNotEqual(h1, h2)
