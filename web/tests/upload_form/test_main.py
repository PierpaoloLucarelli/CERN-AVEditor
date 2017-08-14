import os
from io import BytesIO

from flask import url_for

from web.app import Video
from web.app import path_conversion
from web.tests import BaseTestCase


class UploadFormTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    # make sure that upload is successful when video file submitted is .mp4
    def test_video_upload_mp4(self):
        data = {'filename': 'testfile',
                'file': (BytesIO(b'my file contents'), "111.mp4"),
                'crop_bool': False,
                'crop_start': "",
                'crop_end': ""
             }

        with self.client.session_transaction() as sess:
            sess["user"] = "user"

        response = self.client.post(url_for('video_upload.upload'),
                                    content_type='multipart/form-data',
                                    data=data,
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        video = Video.query.all()
        self.assertEqual(len(video), 1)

    # make sure that upload is un-successful when video file submitted is not .mp4
    def test_video_upload_mp3(self):
        data = {'filename': 'testfile',
                'file': (BytesIO(b'my file contents'), "test.mp3")
                }

        response = self.client.post(url_for('video_upload.upload'),
                                    content_type='multipart/form-data',
                                    data=data,
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 415)

        video = Video.query.all()
        self.assertEqual(len(video), 0)

    # make sure that upload is un-successful when video file isn't provided
    def test_no_video_submitted(self):
        data = {'filename': 'testfile',
                'crop_bool': False,
                'crop_start': "",
                'crop_end': '',
                'file': None
                }

        response = self.client.post(url_for('video_upload.upload'),
                                    content_type='multipart/form-data',
                                    data=data,
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 415)

        video = Video.query.all()
        self.assertEqual(len(video), 0)

    # make sure that main form submission is working correctly
    # def test_main_form_upload(self):
    #     data = {
    #         'video_id': 1,
    #         'crop_bool': False,
    #         'crop_start': '',
    #         'crop_end' :'',
    #         'images': (
    #             (BytesIO(b'my file contents'), "test_mouse.png"),
    #             '00:00:00',
    #             '00:00:02'
    #         )
    #     }
    #
    #     response = self.client.post(url_for('index_page.index'),
    #                                 content_type='multipart/form-data',
    #                                 data=data,
    #                                 follow_redirects=True)
    #
    #     self.assertEqual(response.status_code, 200)

    # make sure that form submission fails if time in wrong format is provided
    def test_wrong_time_format(self):
        data = {'filename': 'testfile',
                'crop_bool': True,
                'crop_start': '10.10.10',
                'crop_end': '10.10.10',
                'file': (BytesIO(b'my file contents'), "test.mp4")}

        with self.client.session_transaction() as sess:
            sess["user"] = "user"
        response = self.client.post(url_for('index_page.index'),
                                    content_type='multipart/form-data',
                                    data=data,
                                    follow_redirects=True)

        self.assertEqual(response.status_code, 500)

        video = Video.query.all()
        self.assertEqual(len(video), 0)

    # test if path conversion is working correctly
    def test_path_conversion(self):
        new_path = path_conversion("/opt/app-root/test.mp4")
        self.assertEqual(os.environ['FFMPEG_FILE_FOLDER'] + "/test.mp4", new_path)