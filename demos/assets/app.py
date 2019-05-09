# -*- coding: utf-8 -*-
'''
@Author: zhou
@Date : 19-5-8 下午5:59
@Desc :
'''
from flask import Flask, render_template
from flask_assets import Environment, Bundle
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.secret_key = 'dev key'
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

assets = Environment(app)
ckeditor = CKEditor(app)

# 注册资源集,分别使用cssmin与jsmin来压缩CSS和JavaScript代码
css = Bundle('css/bootstrap.min.css',
             'css/bootstrap.css',
             'css/dropzone.min.css',
             'css/jquery.Jcrop.min.css',
             'css/style.css',
             filters='cssmin', output='gen/packed.css')

js = Bundle('js/jquery.min.js',
            'js/popper.min.js',
            'js/bootstrap.min.js',
            'js/bootstrap.js',
            'js/moment-with-locales.min.js',
            'js/dropzone.min.js',
            'js/jquery.Jcrop.min.js',
            filters='jsmin', output='gen/packed.js')

assets.register('css_all', css)
assets.register('js_all', js)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/foo')
def unoptimized():
    return render_template('unoptimized.html')


@app.route('/bar')
def optimized():
    return render_template('optimized.html')
