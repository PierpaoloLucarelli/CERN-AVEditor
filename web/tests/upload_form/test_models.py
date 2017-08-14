import datetime

from app.models import Video, Image

from web.app.extensions import db
from web.tests import BaseTestCase


class DatabaseTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    # make sure that video is correctly inserted
    def test_video_insertion(self):
        db.session.add(Video(
            file='url/for/my/file.mp4',
            crop_bool=True,
            crop_start=datetime.time(10, 10, 10),
            crop_end=datetime.time(10, 10, 10)))

        db.session.commit()
        video = Video.query.all()
        self.assertEqual(len(video), 1)

    # add and remove video to test video removal
    def test_remove_video(self):
        new_video = Video(
            file='url/for/my/file.mp4',
            crop_bool=True,
            crop_start=datetime.time(10, 10, 10),
            crop_end=datetime.time(10, 10, 10)
        )
        db.session.add(new_video)
        db.session.commit()

        videos = Video.query.all()
        self.assertEqual(len(videos), 1)

        db.session.delete(videos[0])
        db.session.commit()

        videos = Video.query.all()
        self.assertEqual(len(videos), 0)

    # make sure image is correctly inserted
    def test_add_image(self):
        new_video = Video(
            file='url/for/my/file.mp4',
            crop_bool=True,
            crop_start=datetime.time(10, 10, 10),
            crop_end=datetime.time(10, 10, 10)
        )
        db.session.add(new_video)
        db.session.commit()
        videos = Video.query.all()
        self.assertEqual(len(videos), 1)

        image = Image(
            img_upload="path/to/image",
            pic_start=datetime.time(10, 10, 10),
            pic_stop=datetime.time(10, 10, 10),
            parent_video_id=1
        )
        db.session.add(image)
        db.session.commit()
        images = Image.query.all()
        self.assertEqual(len(images), 1)

    # make sure image is correctly removed
    def test_remove_image(self):
        new_video = Video(
            file='url/for/my/file.mp4',
            crop_bool=True,
            crop_start=datetime.time(10, 10, 10),
            crop_end=datetime.time(10, 10, 10)
        )
        db.session.add(new_video)
        db.session.commit()
        videos = Video.query.all()
        self.assertEqual(len(videos), 1)

        image = Image(
            img_upload="path/to/image",
            pic_start=datetime.time(10, 10, 10),
            pic_stop=datetime.time(10, 10, 10),
            parent_video_id=1
        )
        db.session.add(image)
        db.session.commit()
        images = Image.query.all()
        self.assertEqual(len(images), 1)

        db.session.delete(images[0])
        db.session.commit()

        images = Image.query.all()
        self.assertEqual(len(images), 0)
