# Tests for the FoodPost class
from food_post import FoodPost
import unittest


class DummySubmission:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.url = kwargs.get('url')
        self.permalink = kwargs.get('permalink')
        self.title = kwargs.get('title')
        self.media_metadata = kwargs.get('media_metadata')

class FoodPostTest(unittest.TestCase):
    def test_truncate_does_nothing_for_shorter_title(self):
        title = 'something short'
        self.assertEqual(FoodPost.truncate(title), title)

    def test_truncate_returns_none_for_none_input(self):
        self.assertIsNone(FoodPost.truncate(None))

    def test_truncate_title_that_is_too_long(self):
        truncated_title = 'a' * 253  # the title will be truncated this much
        title = truncated_title + 'aaaaa'  # len(title) > 256
        expected = truncated_title + '...'
        actual = FoodPost.truncate(title)
        self.assertNotEqual(actual, title)
        self.assertEqual(actual, expected)

    def test_transform_reddit_submission_to_food_post(self):
        submission_params = {
            'id': 'foo',
            'url': 'bar',
            'permalink': 'baz',
            'title': 'something'
        }
        fp = FoodPost.from_submission(DummySubmission(**submission_params))
        self.assertIsNotNone(fp)
        self.assertEqual(fp.id, submission_params['id'])
        self.assertEqual(fp.image_url, submission_params['url'])
        self.assertEqual(fp.title, submission_params['title'])
        self.assertEqual(fp.post_url, f'https://www.reddit.com{submission_params["permalink"]}')

    def test_discord_embed_omits_image_if_not_provided(self):
        fp = FoodPost(id='1', title='2', permalink='3')
        em = fp.to_embed()
        self.assertEqual(em["title"], '2')
        self.assertEqual(em["description"], '3')
        self.assertNotIn("image", em)

    def test_discord_embed_truncates_title(self):
        truncated_title = 'a' * 253  # the title will be truncated this much
        title = truncated_title + 'aaaaa'  # len(title) > 256
        expected = truncated_title + '...'
        fp = FoodPost(id='1', title=title, permalink='2', image_url='3')
        em = fp.to_embed()
        self.assertEqual(fp.title, title)
        self.assertEqual(em["title"], expected)
        self.assertEqual(em["description"], '2')
        self.assertEqual(em["image"], {'url': '3'})

    def test_json_with_hash(self):
        fp = FoodPost(id='1')
        d = fp.to_json_with_hash(123)
        self.assertEqual(d['id'], '1')
        self.assertEqual(d['hash'], "123")
    
    def test_derive_image_url_from_gallery(self):
        submission_params = {
            'id': 'foo',
            'url': 'https://www.reddit.com/gallery/bar',
            'permalink': 'baz',
            'title': 'something',
            'media_metadata': {
                'foo1': 1,  # the value here isn't used
                'bar2': 3
            }
        }
        fp = FoodPost.from_submission(DummySubmission(**submission_params))
        self.assertIsNotNone(fp)
        self.assertEqual(fp.image_url, 'https://i.redd.it/bar2.jpg')

    def test_none_url_returns_none(self):
        submission_params = {
            'id': 'foo',
            'permalink': 'baz',
            'title': 'something'
        }
        res = FoodPost.derive_image_url(DummySubmission(**submission_params))
        self.assertIsNone(res)
    
    def test_normal_url_does_not_mutate(self):
        submission_params = {
            'id': 'foo',
            'url': 'bar',
            'permalink': 'baz',
            'title': 'something'
        }
        res = FoodPost.derive_image_url(DummySubmission(**submission_params))
        self.assertEqual(res, submission_params['url'])

    def test_derive_image_url_truncates_query_parameters(self):
        # 
        img_url = 'https://preview.redd.it/chun02can1f81.png?width=640&format=png&auto=webp&s=e05f245a349e5971ced5ed125327bb69fa0a4ccc'
        expected = 'https://preview.redd.it/chun02can1f81.png'
        
        submission_params = {
            'id': 'foo',
            'url': img_url,
            'permalink': 'baz',
            'title': 'something'
        }
        res = FoodPost.derive_image_url(DummySubmission(**submission_params))
        self.assertEqual(res, expected)
    
    def test_empty_metadata_returns_none(self):
        submission_params = {
            'id': 'foo',
            'url': 'https://www.reddit.com/gallery/bar',
            'permalink': 'baz',
            'title': 'something',
            'media_metadata': {}
        }
        res = FoodPost.derive_image_url(DummySubmission(**submission_params))
        self.assertIsNone(res)

    def test_none_metadata_returns_none(self):
        submission_params = {
            'id': 'foo',
            'url': 'https://www.reddit.com/gallery/bar',
            'permalink': 'baz',
            'title': 'something'
        }
        res = FoodPost.derive_image_url(DummySubmission(**submission_params))
        self.assertIsNone(res)
