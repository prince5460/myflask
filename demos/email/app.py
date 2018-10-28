'''
Created by ZhouSp on  2018/10/28.
'''

import os
from flask import Flask, flash, redirect, render_template, url_for
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

__author__ = 'ZhouSp'

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'secret string'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=('ZHOU', os.getenv('MAIL_USERNAME'))
)

mail = Mail(app)


# 通用发信函数
def send_mail(subject, to, body):
    message = Message(subject, recipients=[to], body=body)
    mail.send(message)


# 在视图函数中发送邮件
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        email = form.email.data
        flash('Welcome on borad!')
        send_mail('Subscribe success!', email, 'Hello,thank you.')
        return redirect(url_for('subscribe'))
    return render_template('index.html', form=form)


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     return render_template('index.html')


class SubscribeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')
