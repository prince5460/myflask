'''
Created by ZhouSp 18-10-24.
'''
import click

__author__ = 'zhou'

from flask import Flask

# 创建实例
app = Flask(__name__)


# 注册路由
@app.route('/')
def index():
    return '<H1>Hello,Flask!</H1>'


# 为视图绑定多个url
@app.route('/hi')
@app.route('/hello')
def say_hello():
    return '<h1>Hello,Flask!</h1>'


# 动态Url，并设置默认参数
# 方式一
@app.route('/greet1', defaults={'name': 'Programmer'})
@app.route('/greet1/<name>')  # 动态url
def greet1(name):
    return '<h1>Hello,%s</h1>' % name


# 方式二
@app.route('/greet2')
@app.route('/greet2/<name>')
def greet2(name='Programmer'):
    return '<h1>Hello,%s</h1>' % name


# 自定义命令 flask hello
@app.cli.command()
def hello():
    click.echo("Hello,Human!")
