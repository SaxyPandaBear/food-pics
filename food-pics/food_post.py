from typing import Dict, Optional


GALLERY_URL = 'https://www.reddit.com/gallery/'


class FoodPost:
    # Attributes
    # id - the submission ID given by Reddit
    # title - the Post title
    # post_url - the permalink for this post
    # image_url - the url for the associated image of a submission
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title')
        self.post_url = kwargs.get('permalink')
        self.image_url = kwargs.get('image_url')
        self.color = 0xDB5172

    def __str__(self):
        return f'{self.title} : {self.post_url}'

    def __repr__(self):
        return self.__str__()

    # Transforms this FoodPost object into the discord Embed dictionary that
    # should be posted.
    def to_embed(self) -> Dict:
        data = {
            "title": FoodPost.truncate(self.title),
            "description": self.post_url,
            "color": self.color
        }
        if self.image_url is not None and self.image_url != '':
            data["image"] = {
                "url": self.image_url
            }
        return data

    def to_json_with_hash(self, img_hash: int) -> Dict:
        """
        Transform the submission and it's hash into a Python
        dictionary, so that it can be converted into a JSON string
        that gets persisted in the Redis cache as part of an array.

        Example:
        {
            "id": "foo-bar-baz",
            "hash": "1234567890"
        }
        @param img_hash the hash of the byte array of the Image from PIL
        @return dictionary to be persisted into the Redis cache.
        """
        return {
            "id": self.id,
            "hash": str(img_hash)
        }

    # Given a Reddit submission title, truncate the title if it's too long
    # https://github.com/SaxyPandaBear/discord-food-bot/issues/28
    # If the title is not too long, return the input unchanged
    @staticmethod
    def truncate(title: str) -> str:
        if title is None:
            return None

        # truncate with an ellipsis, so we need some leeway
        if len(title) > 256:
            return title[:253] + '...'  # take first 253 characters
        return title

    # Take a Reddit submission object, and transform that into a FoodPost
    @staticmethod
    def from_submission(submission):
        sub_id = submission.id
        url = FoodPost.derive_image_url(submission)
        # permalink does not give the full URL, so build it instead.
        permalink = f'https://www.reddit.com{submission.permalink}'
        title = submission.title
        return FoodPost(id=sub_id, title=title, image_url=url, permalink=permalink)

    @staticmethod
    def derive_image_url(submission) -> Optional[str]:
        """
        A submission can point to a gallery instead of a direct link to
        an image. This gallery URL does not render properly on Discord in the
        embed. Have to pick one of the images ourselves, and then use that
        to display in this scenario.
        @param submission The submission object from PRAW
        """
        url = submission.url
        if url is not None and url.startswith(GALLERY_URL):
            # https://github.com/SaxyPandaBear/my-webhooks/issues/4
            # If the submission points to a Reddit gallery, need to pick one
            # of the images in the gallery to render in the Discord embed.
            # The set of images are defined in the "media_metadata" attribute
            # of the submission.
            images: Dict = submission.media_metadata
            if images is None or len(images) < 1:
                return None
            # Unsure if ordering is guaranteed, so in order to be 
            # deterministic, ensure ordering on our end by sorting.
            ids = sorted(images)  # this sorts by key, and only returns keys.
            return f'https://i.redd.it/{ids[0]}.jpg'
        else:
            return url
