'''
Created by ZhouSp on  2018/10/28.
'''

import os
import sys
import click

from flask import Flask, flash, redirect, url_for, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

__author__ = 'ZhouSp'

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = os.getenv('SECRET_KEY', 'secret string')

# sqlite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# 配置SqlAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
                                                  prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # 必须先导入参数，再创建db才有效
migrate = Migrate(app, db)


# 注册shell上下文处理函数
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Note=Note, Author=Author, Article=Article, Writer=Writer, Book=Book,
                Singer=Singer, Song=Song, Citizen=Citizen, City=City, Capital=Capital,
                Country=Country, Teacher=Teacher, Student=Student, Post=Post, Comment=Comment, Draft=Draft)


# shell创建数据库
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# 定义数据模型
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Note %r>' % self.body


# 创建表单
class NewNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditNoteForm(NewNoteForm):
    submit = SubmitField('Update')


class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')


@app.route('/')
def index():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template('index.html', form=form, notes=notes)


# 新增
@app.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        return redirect(url_for('index'))

    return render_template('new_note.html', form=form)


# 更新
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('Your note is updated.')
        return redirect(url_for('index'))
    form.body.data = note.body
    return render_template('edit_note.html', form=form)


# 删除
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)  # 获取对应的记录
        db.session.delete(note)  # 删除记录
        db.session.commit()  # 提交修改
        flash('Your note is delete.')
    else:
        abort(404)
    return redirect(url_for('index'))


# 一对多关系
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(20))
    articles = db.relationship('Article')  # 定义属性关系

    def __repr__(self):
        return '<Author %r>' % self.name


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))  # 定义外键

    def __repr__(self):
        return '<Article %r>' % self.title


# 用back_populates建立一对多关系的双向关系
class Writer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    books = db.relationship('Book', back_populates='writer')

    def __repr__(self):
        return '<Writer %r>' % self.name


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('writer.id'))
    writer = db.relationship('Writer', back_populates='books')

    def __repr__(self):
        return '<Book %r>' % self.title


# 使用backref建立双向关系
class Singer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    songs = db.relationship('Song', backref='singer')

    def __repr__(self):
        return '<Singer %r>' % self.name


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    singer_id = db.Column(db.Integer, db.ForeignKey('singer.id'))

    def __repr__(self):
        return '<Song %r>' % self.name


# 建立多对一关系
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')

    def __repr__(self):
        return '<Citizen %r>' % self.name


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return '<City %r>' % self.name


# 建立一对一关系
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    capital = db.relationship('Capital', uselist=False)

    def __repr__(self):
        return '<Country %r>' % self.name


class Capital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')

    def __repr__(self):
        return '<Capital %r>' % self.name


# 建立多对多关系
association_table = db.Table('association',
                             db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                             db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    grade = db.Column(db.String(20))
    teachers = db.relationship('Teacher', secondary=association_table, back_populates='students')  # collection

    def __repr__(self):
        return '<Student %r>' % self.name


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    office = db.Column(db.String(20))
    students = db.relationship('Student', secondary=association_table, back_populates='teachers')  # collection

    def __repr__(self):
        return '<Teacher %r>' % self.name


# 级联操作
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text)
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')  # collection


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')  # scalar


# 事件监听
class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    edit_time = db.Column(db.Integer, default=0)


@db.event.listens_for(Draft.body, 'set')
def increment_edit_time(target, value, oldvalue, initiator):
    if target.edit_time is not None:
        target.edit_time += 1
