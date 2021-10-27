# Tests for the FoodPost class
from food_post import FoodPost
from typing import Dict
import unittest


class DummySubmission:
    def __init__(self, params: Dict):
        self.id = params['id']
        self.url = params['url']
        self.permalink = params['permalink']
        self.title = params['title']

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
        fp = FoodPost.from_submission(DummySubmission(submission_params))
        self.assertIsNotNone(fp)
        self.assertEqual(fp.id, submission_params['id'])
        self.assertEqual(fp.image_url, submission_params['url'])
        self.assertEqual(fp.title, submission_params['title'])
        self.assertEqual(fp.post_url, f'https://www.reddit.com{submission_params["permalink"]}')


    def test_discord_embed_omits_image_if_not_provided(self):
        fp = FoodPost(id='1', title='2', permalink='3')
        em = fp.to_embed()
        self.assertEqual(em.title, '2')
        self.assertEqual(em.description, '3')
        self.assertEqual(em._image, {'url': 'None'})


    def test_discord_embed_truncates_title(self):
        truncated_title = 'a' * 253  # the title will be truncated this much
        title = truncated_title + 'aaaaa'  # len(title) > 256
        expected = truncated_title + '...'
        fp = FoodPost(id='1', title=title, permalink='2', image_url='3')
        em = fp.to_embed()
        self.assertEqual(fp.title, title)
        self.assertEqual(em.title, expected)
        self.assertEqual(em.description, '2')
        self.assertEqual(em._image, {'url': '3'})