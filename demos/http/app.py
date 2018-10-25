'''
Created by ZhouSp 18-10-24.
'''
__author__ = 'zhou'

from flask import Flask, request, redirect, url_for, abort, make_response, json, jsonify, session
from urllib.parse import urlparse, urljoin
from jinja2.utils import generate_lorem_ipsum
from jinja2 import escape
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')


@app.route('/hello')
def hello():
    name = request.args.get('name', 'Flask')  # 获取查询参数name的值
    # return '<h1>Hello,%s</h1>' % name  # 插入到返回值中
    return '<h1>Hello,%s</h1>' % escape(name)  # 对用户传入的数据进行转义


# url变量转换int,float,string,path,any,uuid
@app.route('/goback/<int:year>')
def go_back(year):
    return '<h1>Welcome to %d!</h1>' % (2018 - year)


# 使用 any URL 转换器
@app.route('/colors/<any(blue, white, red):color>')
def three_colors(color):
    return '<h1>I like %s.</h1>' % color


# 指定不同的状态码
@app.route('/hi')
def hi():
    return "<h1>Hello,Flask!</h1>", 201


# 重定向
@app.route('/good')
def good():
    # return '', 302, {'Location': "https://www.baidu.com"}
    # return redirect('https://www.baidu.com')
    return redirect(url_for('hi'))  # 重定向到其他视图


# 返回错误响应
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'


# 返回404错误响应
@app.route('/404')
def not_found():
    abort(404)


# 设置响应格式,纯文本:text/plain,HTML:text/html,XML:application/xml,JSON:application/json
@app.route('/ho')
def ho():
    response = make_response("Hello,World!")  # 生成响应对象
    response.mimetype = 'text/html'
    return response


@app.route('/ho_json')
def ho_json():
    data = {
        'name': 'zhou',
        'gender': 'male'
    }
    # 使用json.dumps转换成json
    # response = make_response(json.dumps(data))
    # response.mimetype = 'application/json'
    # return response

    # 使用jsonify转换成json,jsonify()可接收多种形式参数
    # return jsonify(data)
    # return jsonify(name='zhou', gender='male')
    return jsonify(message='Error!'), 500  # jsonify可附加状态码来自定义响应类型


# 不同格式的返回响应
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''
                Note
                to: Peter
                from: Jane
                heading: Reminder
                body: Don't forget the party!
                '''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
                <html>
                <head></head>
                <body>
                  <h1>Note</h1>
                  <p>to: Peter</p>
                  <p>from: Jane</p>
                  <p>heading: Reminder</p>
                  <p>body: <strong>Don't forget the party!</strong></p>
                </body>
                </html>
                '''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
                <note>
                  <to>Peter</to>
                  <from>Jane</from>
                  <heading>Reminder</heading>
                  <body>Don't forget the party!</body>
                </note>
                '''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# 设置cookie
@app.route('/set/<name>')
def set_cookie(name):
    reponse = make_response(redirect(url_for('hello2')))
    reponse.set_cookie('name', name)
    return reponse


# 获取Cookie中存储的name的值
@app.route('/hello2')
def hello2():
    name = request.args.get('name')  # 获取查询参数name的值
    if name is None:
        name = request.cookies.get('name')  # 从Cookies中获取name值
    return '<h1>Hello,%s</h1>' % name  # 插入到返回值中


# 使用session模拟用户认证
@app.route('/login')
def login():
    session['logged_in'] = True  # 写入session
    return redirect(url_for('user'))


@app.route('/user')
def user():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Flask')
        response = '<h1>Hello,%s</h1>' % name
        # 根据用户认证状态返回不同的内容
        if 'logged_in' in session:
            response += '[Authenticated]'
        else:
            response += '[Not Authenticated]'
        return response


# 模拟管理后台
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return "Welcome to admin page."


# 登出
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('user'))


# 重定向回上一个页面
@app.route('/foo')
def foo():
    return '<h1>Foo Page</h1><a href="%s">Do something and redirect</a>' % url_for('do_something',
                                                                                   next=request.full_path)


@app.route('/bar')
def bar():
    return '<h1>Bar Page</h1><a href="%s">Do something and redirect</a>' % url_for('do_something',
                                                                                   next=request.full_path)


# @app.route('/do_something')
@app.route('/do_something_and_redirect')
def do_something():
    # do_something
    # return redirect(url_for('hello'))
    return redirect_back()


# 验证url安全性
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


# 显示虚拟文章
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)  # 生成两段随机文本
    return '''
    <h1>A very long post</h1>
    <div class="body">%s</div>
    <button id="load">Load More</button>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script type="text/javascript">
    $(function(){
        $('#load').click(function(){
            $.ajax({
                url:'/more',                //目标url
                type:'get',                 //请求方法
                success:function(data){     //返回成功响应后触发的回调函数
                    $('.body').append(data);//将返回的响应插入到页面中
                }
            })
        })
    })
    </script>
    ''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)
