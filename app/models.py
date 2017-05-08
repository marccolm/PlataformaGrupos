from flask import current_app, redirect, url_for, request, session
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
import json


class User(UserMixin, db.Model):
	__tablename__='users'
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(64), nullable=True)
	username = db.Column(db.String(64))
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	password_hash = db.Column(db.String(128))
	profile_picture = db.Column(db.String(255))
	bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User: %r>' % self.username

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))