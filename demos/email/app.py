'''
Created by ZhouSp on  2018/10/28.
'''

import os
from flask import Flask, flash, redirect, render_template, url_for, request
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
import sendgrid
from sendgrid.helpers.mail import Email as SGEmail, Content, Mail as SGMail
from threading import Thread

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
def send_smtp_mail(subject, to, body):
    message = Message(subject, recipients=[to], body=body)
    mail.send(message)


# 使用SendGridAPI发送邮件的通用函数
def send_api_mail(subject, to, body):
    sg = sendgrid.SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY'))
    from_email = SGEmail('ZHOU <noreply@zhouhy.com>')
    to_email = SGEmail(to)
    content = Content('text/plain', body)
    mail = SGMail(from_email, subject, to_email, content)
    sg.client.mail.send.post(request_body=mail.get())


# 异步发送邮件
def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_async_mail(subject, to, body):
    message = Message(subject, recipients=[to], body=body)
    thread = Thread(target=_send_async_mail, args=[app, message])
    thread.start()
    return thread


# send email with HTML body
def send_subscribe_mail(subject, to, **kwargs):
    message = Message(subject, recipients=[to], sender='Flask Weekly <%s>' % os.getenv('MAIL_USERNAME'))
    message.body = render_template('emails/subscribe.txt', **kwargs)
    message.html = render_template('emails/subscribe.html', **kwargs)
    mail.send(message)


class EmailForm(FlaskForm):
    to = StringField('To', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    submit_smtp = SubmitField('Send with SMTP')
    submit_api = SubmitField('Send with SendGrid API')
    submit_async = SubmitField('Send with SMTP asynchronously')


class SubscribeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        to = form.to.data
        subject = form.subject.data
        body = form.body.data
        if form.submit_smtp.data:
            send_smtp_mail(subject, to, body)
            method = request.form.get('submit_smtp')
        elif form.submit_api.data:
            send_api_mail(subject, to, body)
            method = request.form.get('submit_api')
        else:
            send_async_mail(subject, to, body)
            method = request.form.get('submit_async')

        flash('Email sent %s! Check your inbox.' % ' '.join(method.split()[1:]))
        return redirect(url_for('index'))
    form.subject.data = 'Hello, World!'
    form.body.data = 'Across the Great Wall we can reach every corner in the world.'
    return render_template('index.html', form=form)


# 在视图函数中发送邮件
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        send_subscribe_mail('Subscribe Success!', email, name=name)
        flash('Confirmation email have been sent! Check your inbox.')
        return redirect(url_for('subscribe'))
    return render_template('subscribe.html', form=form)


@app.route('/unsubscribe')
def unsubscribe():
    flash('Want to unsubscribe? No way...')
    return redirect(url_for('subscribe'))
