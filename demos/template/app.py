'''
Created by ZhouSp 18-10-25.
'''
__author__ = 'zhou'

from flask import Flask, render_template, Markup, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'secret string'

user = {
    'username': 'Grey Li',
    'bio': 'A boy who loves movies and music.',
}

movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'},
]


@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)


@app.route('/')
def index():
    return render_template('index.html')


# 自定义上下文
@app.context_processor
def inject_foo():
    foo = 'I am foo.'
    return dict(foo=foo)  # 等同于return {'foo':foo}


# # 也可以直接调用
# def inject_foo():
#     foo = 'I am foo.'
#     return dict(foo=foo)
#
# app.context_processor(inject_foo)

# 使用lambda简化
# app.context_processor(lambda: dict(foo='I am foo.'))

# 自定义全局函数
@app.template_global()
def bar():
    return 'I am bar.'


# 注册自定义过滤器
@app.template_filter()
def musical(s):
    return s + Markup(' &#9835;')


# 注册自定义测试器
@app.template_test()
def baz(n):
    if n == 'baz':
        return True
    return False


@app.route('/watchlist2')
def watchlist_with_static():
    return render_template('watchlist_with_static.html', user=user, movies=movies)


# 消息闪现
@app.route('/flash')
def just_flash():
    flash('I am flash,who is looking for me?')
    return redirect(url_for('index'))


# 自定义错误页面
# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
