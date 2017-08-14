from app.extensions import video, db, setup_custom_logger
from app.models import Video
from app.utils.ffmpeg import FfmpegTaskRunner
from flask import Blueprint, json, session

from app.upload_form import VideoForm

video_upload = Blueprint('video_upload', __name__,
                         template_folder='templates')

logger = setup_custom_logger('root')


@video_upload.route("/upload", methods=['POST'])
def upload():
    logger.debug('Received POST request to /upload endpoint')
    form = VideoForm()
    if form.validate_on_submit():
        logger.debug('Form was validated')
        file = form.data['file']
        file.filename = "{}.mp4".format("vid")

        # save video info to DB
        vid = Video()
        save_video_to_db(vid, file.filename)

        # save video to FS
        video.save(file, str(vid.id))
        logger.debug('Saved %s to the FileSystem', file.filename)

        # run ffprobe on remote machine to get JSON video details
        output = run_ffmpeg(vid, file.filename)

        # update the video resolution in db
        for stream in output['streams']:
            if stream['codec_type'] == 'video':
                width = stream['width']
                height = stream['height']
                break

        update_video_resolution(vid, width, height)

        if output['success']:
            output['format']['filename'] = file.filename
            output['video_id'] = vid.id
            return json.dumps(output), 200, {'ContentType': 'application/json'}

        return json.dumps({
            'success': False,
            'err': "Something went wrong"
        }), 500, {'ContentType': 'application/json'}

    logger.error('Form validation unsuccessful')
    logger.error('WTFFORMS errors: %s\n', form.errors)
    return json.dumps({
        'success': False,
        'err': "File format not allowed"
    }), 415, {'ContentType': 'application/json'}


def save_video_to_db(vid, filename):
    """
    Saves the video file to the Database
    :param vid: The video model instance that will be saved to the Database (app.models.Video)
    :param filename: The name of the file that
    """
    vid.file = filename
    vid.person_id = session.get('user', None)['person_id']
    db.session.add(vid)
    db.session.commit()
    logger.debug('Saved %s to the Database', filename)


def run_ffmpeg(vid, filename):
    """
    Will create and run the ffmpeg command
    :param vid: The video model instance (app.models.Video)
    :param filename: The name of the file used by the ffmpeg command
    :return: a JSON object containing the stdout of the ffmpeg command
    """
    task_runner = FfmpegTaskRunner()
    cmd = task_runner.ffprobe(str(vid.id), filename)

    output = task_runner.ffmpeg_run(cmd)
    return output


def update_video_resolution(vid, width, height):
    """
    updates the current video with the resolution received from ffprobe
    :param vid: current video (app.models.video)
    :param width: width of video
    :param height: height of video
    """
    vid.width = width
    vid.height = height
    db.session.commit()

