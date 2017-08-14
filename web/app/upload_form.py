from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import FieldList, HiddenField, IntegerField
from wtforms.fields import BooleanField, StringField, FormField, FileField, RadioField
from wtforms.validators import DataRequired, Optional, NumberRange

from app.extensions import images, video, time_regex


# custom validator to validate on condition
class RequiredIf(DataRequired):
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        # if other_field contains data then "field" will be required
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


# custom validator to validate on condition
# will only require
class ImageRequiredIf(DataRequired):
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(ImageRequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        print(other_field.data)
        if other_field.data:
            super(ImageRequiredIf, self).__call__(form, field)


class ImageForm(FlaskForm):
    img_upload = FileField(u'Video File', validators=[FileAllowed(images, 'Images only!')])
    duration = IntegerField("Pic Stop", validators=[ImageRequiredIf('img_upload'), Optional(), NumberRange()])
    slide_type = RadioField('Slide Type', choices=[('intro','Intro slide'),('outro','Outro slide')], default='intro')


class UploadForm(FlaskForm):
    video_id = HiddenField("Video id", validators=[DataRequired()])
    crop_bool = BooleanField('Crop Video', default=False)
    crop_start = StringField('Start Crop',
                             validators=[RequiredIf('crop_bool'), Optional(), time_regex],
                             filters=[lambda x: x or None])
    crop_end = StringField('Stop Crop',
                           validators=[RequiredIf('crop_bool'), Optional(), time_regex],
                           filters=[lambda x: x or None])
    # min_entries=1 ensures that the image form will show at least once
    images = FieldList(FormField(ImageForm), min_entries=1)


class VideoForm(FlaskForm):
    # video upload form
    file = FileField(u'Video File', validators=[FileRequired(), FileAllowed(video, 'Videos only!')])
