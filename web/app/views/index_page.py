import os

from app.extensions import images, db, setup_custom_logger
from app.models import Image, Video
from app.upload_form import UploadForm, VideoForm
from app.utils.ffmpeg import FfmpegTaskRunner
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_uploads import UploadNotAllowed

from app.utils import mailer

index_page = Blueprint('index_page', __name__,
                       template_folder='templates')

logger = setup_custom_logger('root')


@index_page.route("/", methods=['GET', 'POST'])
def index():
    current_user = session.get('user', None)
    form = UploadForm()  # main form
    video_form = VideoForm()  # video form

    if request.method == 'POST':
        logger.debug('Received a request DATA: ', form.data)
        # validate main form
        if form.validate_on_submit():
            job_id = form.data['video_id']

            # make a list of all images in the form and save them to db
            image_list = generate_image_list(form, job_id)
            save_form_to_db(form.data, image_list)

            if form.data['crop_bool']:
                # cut the video
                output = ffmpeg_cut_video(job_id, form)
                if not output['success']:
                    return render_template('index.html',
                                           form=form,
                                           video_form=video_form,
                                           user=current_user,
                                           err="Video crop was unsuccessful"), 500

            # get video by id and it's images, then merge them in one video
            video = Video.query.get(job_id)
            slides = Image.query.filter_by(parent_video_id=job_id).all()
            if len(slides) >= 1:
                concat_images_to_video(slides, video, job_id)
            mailer.send_email(current_user, job_id)
            return render_template('job_submitted.html',
                                   user=current_user)

        # if form didn't pass the wtfForm validation
        return render_template('index.html',
                               form=form,
                               video_form=video_form,
                               user=current_user,
                               err=form.errors), 500
    # show empty form on GET request
    return render_template('index.html',
                           form=form,
                           video_form=video_form,
                           user=current_user)


@index_page.route('/logout')
def logout():
    """
    View to log out a user on the site
    :return: Redirects to the index_page.index after logout
    """
    session["user"] = None
    return redirect(url_for('index_page.index'))


def form_has_one_image(data):
    """
    Returns True if passed form contains at least one image
    :param data: data coming from posted request
    :return:

    """
    file = data['images'][0]['img_upload']
    if not file or not file.filename:
        return False
    else:
        return True


def generate_image_list(form, job_id):
    """
    Will generate a list of image model instances (app.models.Image)
    :param form: The form containing the data from the client POST request
    :param job_id: The id of the job that can be retrieved from the database
    :return: A list of images
    """
    image_list = []
    if form_has_one_image(form.data):
        for image_form in form.data['images']:
            img = init_image(image_form, job_id)
            if img:
                image_list.append(img)
    return image_list


def init_image(img_form, job_id):
    """
    Will save the image to the FS and prepares the image objects to be save in the db
    :param img_form: Form data for one image
    :return: Image object
    """
    try:
        images.save(img_form['img_upload'], job_id + "/img")
        image = Image()
        image.img_upload = img_form['img_upload'].filename
        image.duration = img_form['duration']
        image.slide_type = img_form['slide_type']

    except UploadNotAllowed:
        return None

    return image


def save_form_to_db(form, images):
    """
    Will add the video id as a foreign key of the images and save all to the Database, Crop details may be added
    if crop_bool is True
    :param form: The form coming from the client POST request
    :param images: a List of app.models.Video Objects
    """
    vid = Video.query.get(form['video_id'])
    if form['crop_bool']:
        vid.crop_bool = True
        vid.crop_start = form['crop_start']
        vid.crop_end = form['crop_end']
    vid.images.extend(images)
    db.session.add_all(images)
    db.session.add(vid)
    db.session.commit()


def ffmpeg_cut_video(job_id, form):
    """
    WIll cut a video given start and stop time
    :param job_id: the id of the video (app.models.Video.id)
    :param form: client POST form
    :return: returns JSON data coming from command execution and success flag
    """
    task_runner = FfmpegTaskRunner()
    cmd = task_runner.ffmpeg_cut_video(
        job_id,
        "vid.mp4",
        form.data['crop_start'],
        form.data['crop_end']
    )
    output = task_runner.ffmpeg_run(cmd)
    os.remove(os.environ['UPLOADED_VIDEO_DEST'] + job_id + "/vid.mp4")
    os.rename(os.environ['UPLOADED_VIDEO_DEST'] + job_id + "/vid_cut.mp4",
              os.environ['UPLOADED_VIDEO_DEST'] + job_id + "/vid.mp4")
    return output


def concat_images_to_video(slides, video, job_id):
    """
    Will run an ffmpeg command to concat images and video in one video
    :param slides: slides to attach to the video
    :param video: Main video
    :param job_id: Id of the video
    :return: JSON data containing success flag of operations
    """
    # create output folder
    os.makedirs(os.environ['VIDEO_OUTPUT_DEST'] + str(video.id))
    task_runner = FfmpegTaskRunner()
    # generates string containing the ffmpeg command
    cmd = task_runner.concat_images_to_video(slides, video, job_id)
    return task_runner.ffmpeg_run(cmd)
