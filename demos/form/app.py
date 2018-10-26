'''
Created by ZhouSp 18-10-26.
'''
import uuid

__author__ = 'zhou'

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_babel import Babel
from forms import LoginForm, UploadForm

app = Flask(__name__)
app.secret_key = 'secret string'

# 配置上传文件路径
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')

# Flask config
# set request body's max length
# app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3Mb

# 设置内置错误提示语言为中文
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
babel = Babel(app)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/basic', methods=['GET', 'POST'])
def basic():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        flash('Welcome home, %s' % username)
        return redirect(url_for('index'))
    return render_template('basic.html', form=form)


@app.route('/bootstrap')
def bootstrap():
    form = LoginForm()
    return render_template('bootstrap.html', form=form)


# 重命名文件
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


# 处理上传文件
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success.')
        session['filenames'] = [filename]
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)


@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')
