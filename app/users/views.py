import os
from flask import render_template, redirect, request, url_for, flash, current_app, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
from werkzeug.security import safe_join
from . import users
from .. import db
from .. import config
from .forms import RegistrationForm, LoginForm, EditProfileInfoForm
from ..models import User

@users.route('/index', methods=['GET', 'POST'])
def index_users():
	return render_template('users/index.html')

@users.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data,
					password=form.password.data,
					first_name=form.first_name.data,
					last_name=form.last_name.data)
		if form.profile_picture.data:
			file = request.files[form.profile_picture.name]
			username = form.username.data
			picture_name = add_profile_picture(username, file)
			user.profile_picture = picture_name			
		db.session.add(user)
		db.session.commit()
		login_user(user)

		return redirect(url_for('main.index'))
	return render_template('users/register.html', form=form)

@users.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileInfoForm()
	if form.validate_on_submit():
		valid = True
		if not current_user.verify_password(form.current_password.data):
			flash('Invalid current password')
			valid = False
		if form.username.data != current_user.username:
			another_user = User.query.filter_by(username=form.username.data).first()
			if another_user:
				flash('Username already exists.')
				valid = False
		if valid:
			current_username = current_user.username
			current_user.username = form.username.data
			current_user.first_name = form.first_name.data
			current_user.last_name = form.last_name.data
			if form.password.data:
				current_user.password = form.password.data
			change_user_username_folder(current_username, form.username.data)
			if form.profile_picture.data:
				file = request.files[form.profile_picture.name]
				username = form.username.data
				picture_name = add_profile_picture(username, file)
				current_user.profile_picture = picture_name	
			db.session.add(current_user)
			db.session.commit()
			return redirect(url_for('main.profile'))
	form.username.data = current_user.username
	form.first_name.data = current_user.first_name
	form.last_name.data = current_user.last_name
	return render_template('users/edit_user_info.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(url_for('main.index'))
		flash('Invalid username or password')
		print("could not login")
	return render_template('users/login.html', form=form)

@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('users.login'))

@users.route('/uploads/<username>/<filename>')
def get_file(filename, username):
	filename = safe_join(os.path.join(username), filename)
	upload_folder = safe_join(os.path.join(os.getcwd()), current_app.config['UPLOAD_FOLDER'])
	print(filename)
	return send_from_directory(upload_folder, filename)

""" Facebook SignIn """

@users.route('/login/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('main.index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@users.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('main.index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username = oauth.callback()
	print
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('main.index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		user = User(social_id=social_id, username=username)
		db.session.add(user)
		db.session.commit()
	login_user(user, True)
	return redirect(url_for('main.index'))







