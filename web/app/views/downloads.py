import os

from app.models import Video
from flask import Blueprint, session, send_from_directory

from app.extensions import setup_custom_logger

downloads = Blueprint('downloads', __name__,
                      template_folder='templates')

logger = setup_custom_logger('root')


# sends the video to the owning user
@downloads.route("/downloads/<job_id>", methods=['GET'])
def download(job_id):
    current_user = session.get('user', None)
    vid = Video.query.get(job_id)
    # check if current user is owner of the video
    if current_user and vid.person_id == current_user['person_id']:
        uploads = os.environ['VIDEO_OUTPUT_DEST'] + job_id + "/"
        return send_from_directory(directory=uploads, filename='output.mp4')
    return "permission denied"
