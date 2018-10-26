'''
Created by ZhouSp 18-10-26.
'''
__author__ = 'zhou'

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


# 自定义验证器
# 全局验证器
def is_42(message=None):
    if message is None:
        message = 'Must be 42.'

    def _is_42(form, field):
        if field.data != 42:
            raise ValidationError(message)

    return _is_42


# 行内验证器,针对特定字段的验证器
class FortyTwoForm(FlaskForm):
    answer = IntegerField('The Number', validators=[is_42()])
    submit = SubmitField()

    # def validate_answer(form, field):
    #     if field.data != 42:
    #         raise ValidationError('Must be 42.')


class UploadForm(FlaskForm):
    photo = FileField('Upload Image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField()
