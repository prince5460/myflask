'''
Created by ZhouSp 18-10-26.
'''
import uuid

__author__ = 'zhou'

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_babel import Babel
from .forms import LoginForm, FortyTwoForm, UploadForm, MultiUploadForm, RichTextForm, NewPostForm, SigninForm, \
    RegisterForm, SigninForm2, RegisterForm2
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from flask_ckeditor import CKEditor, upload_fail, upload_success
from flask_dropzone import Dropzone

app = Flask(__name__)
# app.secret_key = 'secret string'
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# 配置上传文件路径
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = ['png', 'jpg', 'jpeg', 'gif']

# Flask config
# set request body's max length
# app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3Mb

# 设置内置错误提示语言为中文
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'

# Flask-CKEditor 配置
app.config['CKEDITOR_SERVE_LOCAL'] = True  # 使用内置的本地资源
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload_for_ckeditor'  # 处理上传文件的URL或端点

# Flask-Dropzone config
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILE_SIZE'] = 3
app.config['DROPZONE_MAX_FILES'] = 30

babel = Babel(app)
ckeditor = CKEditor(app)
dropzone = Dropzone(app)


@app.route('/')
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


# 自定义验证器
@app.route('/custom-validator', methods=['GET', 'POST'])
def custom_validator():
    form = FortyTwoForm()
    if form.validate_on_submit():
        flash('Bingo!')
        return redirect(url_for('index'))
    return render_template('custom_validator.html', form=form)


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


# 获取上传后的文件
@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


# 显示图片
@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')


#  验证文件类型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 处理多文件上传
@app.route('/multi-upload', methods=['GET', 'POST'])
def multi_upload():
    form = MultiUploadForm()
    if request.method == 'POST':
        filenames = []
        # 验证csrf令牌
        try:
            validate_csrf(form.csrf_token.data)
        except ValidationError:
            flash('CSRF token error!')
            return redirect(url_for('multi_upload'))
        # 检查文件是否存在
        if 'photo' not in request.files:
            flash('This field is required.')
            return redirect(url_for('multi_upload'))

        for f in request.files.getlist('photo'):
            if f and allowed_file(f.filename):
                filename = random_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                filenames.append(filename)
            else:
                flash('Invalid file type.')
                return redirect(url_for('multi_upload'))
        flash('Upload sucess.')
        session['filenames'] = filenames
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)


# 富文本编辑器
@app.route('/ckeditor', methods=['GET', 'POST'])
def integrate_ckeditor():
    form = RichTextForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        flash("Your post is published.")
        return render_template('post.html', title=title, body=body)
    return render_template('ckeditor.html', form=form)


# 富文本编辑器的图片本地上传
@app.route('/upload-ck', methods=['POST'])
def upload_for_ckeditor():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
    url = url_for('get_file', filename=f.filename)
    return upload_success(url, f.filename)


# 单个表单多个提交按钮
@app.route('/two-submits', methods=['GET', 'POST'])
def two_submits():
    form = NewPostForm()
    if form.validate_on_submit():
        if form.save.data:
            # save it...
            flash('You click the "Save" button.')
        elif form.publish.data:
            # publish it...
            flash('You click the "Publish" button.')
        return redirect(url_for('index'))
    return render_template('2submit.html', form=form)


# 在视图函数中处理多个表单
@app.route('/multi-form', methods=['GET', 'POST'])
def multi_form():
    signin_form = SigninForm()
    register_form = RegisterForm()

    if signin_form.submit1.data and signin_form.validate():
        username = signin_form.username.data
        flash('{},you just submit the Signin Form.'.format(username))
        return redirect(url_for('index'))

    if register_form.submit2.data and register_form.validate():
        username = register_form.username.data
        flash('{},you just submit the Register Form.'.format(username))
        return redirect(url_for('index'))

    return render_template('2form.html', signin_form=signin_form, register_form=register_form)


# 多视图函数
@app.route('/multi_form_multi_view')
def multi_form_multi_view():
    signin_form = SigninForm2()
    register_form = RegisterForm2()
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


# 使用单独多视图函数处理表单提交多POST请求
@app.route('/handle-signin', methods=['GET', 'POST'])
def handle_signin():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if signin_form.validate_on_submit():
        username = signin_form.username.data
        flash('%s,you just submit Signin Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/handle-handle_register', methods=['GET', 'POST'])
def handle_register():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if register_form.validate_on_submit():
        username = register_form.username.data
        flash('%s,you just submit Register Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


# 拖拽上传图片
@app.route('/dropzone-upload', methods=['GET', 'POST'])
def dropzone_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'This field is required.', 400
        f = request.files.get('file')

        if f and allowed_file(f.filename):
            filename = random_filename(f.filename)
            f.save(os.path.join(
                app.config['UPLOAD_PATH'], filename
            ))
        else:
            return 'Invalid file type.', 400
    return render_template('dropzone.html')
