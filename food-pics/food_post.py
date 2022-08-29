from datetime import datetime
from image_util import compute_image_hash
from typing import Dict, Optional


GALLERY_URL = "https://www.reddit.com/gallery/"
DATETIME_FMT = "%d/%m/%y %H:%M"


class FoodPost:
    # Attributes
    # id - the submission ID given by Reddit
    # author - the author of the submission
    # title - the post title
    # post_url - the permalink for this post
    # image_url - the url for the associated image of a submission
    # img_hash - (for testing only) the hash of the image bytes array
    # created_utc - timestamp that the post was created
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.author = kwargs.get("author")
        self.title = kwargs.get("title")
        self.post_url = kwargs.get("permalink")
        self.image_url = kwargs.get("image_url")
        self.img_hash = kwargs.get("img_hash")  # for testing
        self.color = 0xDB5172
        ts = kwargs.get("created_utc")
        if ts is not None and ts > 0:
            self.date_posted = datetime.fromtimestamp(ts)
        else:
            self.date_posted = None
        ts = kwargs.get("date_found")
        if ts is not None and ts > 0:
            # For testing only
            self.date_found = datetime.fromtimestamp(ts)
        else:
            # default to now timestamp in non-test cases
            self.date_found = datetime.now()

    def __str__(self):
        return f"{self.title} : {self.post_url}"

    def __repr__(self):
        return self.__str__()

    # Transforms this FoodPost object into the discord Embed dictionary that
    # should be posted.
    def to_embed(self) -> Dict:
        data = {
            "title": FoodPost.truncate(self.title),
            "description": self.post_url,
            "color": self.color,
        }
        if self.image_url is not None and self.image_url != "":
            data["image"] = {"url": self.image_url}
        return data

    def image_hash(self) -> int:
        if self.img_hash is None:
            self.img_hash = compute_image_hash(self.image_url)
        return self.img_hash

    def to_json(self) -> Dict:
        """
        Transform the submission and it's hash into a Python
        dictionary, so that it can be converted into a JSON string
        that gets persisted in the database.

        Example:
        {
            "id": "foo-bar-baz",
            "author": "person123"
            "img": "1234567890",
            "title" "Something here",
            "posted": "2022-01-01",
            "found": "2022-08-01"
        }
        @return dictionary to be persisted into the database.
        """
        return {
            "id": self.id,
            "author": self.author,
            "img": str(self.image_hash()),
            "title": self.title,
            "posted": self.date_posted.strftime(DATETIME_FMT),
            "found": self.date_found.strftime(DATETIME_FMT),
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
            return title[:253] + "..."  # take first 253 characters
        return title

    # Take a Reddit submission object, and transform that into a FoodPost
    @staticmethod
    def from_submission(submission):
        sub_id = submission.id
        author = submission.author.name
        url = FoodPost.derive_image_url(submission)
        # permalink does not give the full URL, so build it instead.
        permalink = f"https://www.reddit.com{submission.permalink}"
        title = submission.title
        created_utc = submission.created_utc

        # for testing only
        try:
            found_ts = submission.test_date_found
        except AttributeError:
            found_ts = None  # Default to this if submission isn't a dummy obj

        return FoodPost(
            id=sub_id,
            author=author,
            title=title,
            image_url=url,
            permalink=permalink,
            created_utc=created_utc,
            date_found=found_ts,
        )

    @staticmethod
    def derive_image_url(submission) -> Optional[str]:
        """
        A submission can point to a gallery instead of a direct link to
        an image. This gallery URL does not render properly on Discord in the
        embed. Have to pick one of the images ourselves, and then use that
        to display in this scenario.
        @param submission The submission object from PRAW
        """
        if submission is None or submission.url is None:
            return None

        url = submission.url
        if url.startswith(GALLERY_URL):
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
            url = f"https://i.redd.it/{ids[0]}.jpg"

        query_param_idx = url.find("?")
        if query_param_idx >= 0:
            url = url[:query_param_idx]
        return url
