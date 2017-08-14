from app.extensions import db


class Video(db.Model):
    """
    Represents the data for the uploaded video
    """

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer)
    file = db.Column(db.String(255), nullable=False)
    crop_bool = db.Column(db.Boolean, nullable=False, default=False)
    crop_start = db.Column(db.String(255))
    crop_end = db.Column(db.String(255))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    images = db.relationship('Image')


class Image(db.Model):
    """
    Represents an image attached to the video file
    """

    id = db.Column(db.Integer, primary_key=True)
    img_upload = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer)
    slide_type = db.Column(db.String(15), nullable=False)
    parent_video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
