from flask import render_template, redirect, request, url_for, flash, make_response, current_app, send_from_directory
from flask.ext.login import login_required, logout_user, current_user
from . import main
from .. import db
from ..models import User

import re
import os
import urllib
import string
from werkzeug import secure_filename
from werkzeug.security import safe_join

@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated():
        categories = get_categories()
        return render_template('index.html', categories=categories)
    else:
        return redirect(url_for('users.login'))

@main.route('/profile')
@login_required
def profile():
    categories = get_categories()
    bookmarks_count = get_bookmarks_count_dict(categories)
    social_id = ""
    if current_user.social_id:
        social_id = current_user.social_id.split('$')[1]
    return render_template('profile.html', categories=categories,
                            bookmarks_count=bookmarks_count,
                            social_id=social_id)

@main.route('/bookmarks/<category_id>')
@login_required
def bookmarks(category_id):
    category = Category.query.filter_by(id=category_id).first()
    category_name = ""
    if category:
        category_name = category.name
    categories = get_categories()
    bookmarks = get_bookmarks(category_id)
    return render_template('bookmarks.html', bookmarks=bookmarks,
                            categories=categories,
                            category_name=category_name,
                            category_id=category_id)

@main.route('/add_bookmark',  methods=['GET', 'POST'])
@login_required
def add_bookmark():
    
    grabzIt = GrabzItClient.GrabzItClient("OTU1ODEwNTVmZGU0NDMyNmE0NWRlZThkMDQ0NWViN2I=", "PD9VPz8/KD9VPyk/P0dNPyE/Pz8NPz8/Oz8IPxI/Lj8=")

    categories = get_categories()
    form = BookmarkForm()
    path = '/uploads/bookmarks'
    if form.validate_on_submit():
        url = form.link.data
        page = crawl(url)
        if page:
            title = page['title']
            description = page['description'][:150]
            txt = page['txt']
            name_category = estimator.predict([txt])[0]
            category = Category.query.filter_by(name=name_category).first()
            bookmark = Bookmark(link=url, title=title, description=description,
                                user_id=current_user.id, category_id=category.id)
            db.session.add(bookmark)
            db.session.commit()

            grabzIt.SetImageOptions(bookmark.link)
            directory = safe_join(os.path.join(current_app.config['UPLOAD_FOLDER']), "bookmarks")
            if not os.path.exists(directory):
                print("No existe")
                os.makedirs(directory)
            extension = '.jpg'
            picture_name = "%i%s" % (bookmark.id, extension)
            path_picture = safe_join(os.path.join(directory), picture_name)
            grabzIt.SaveTo(path_picture) 

            flash_message = '%s was added to %s category' % (title, category.name)
            flash(flash_message)
            return redirect(url_for('main.add_bookmark'))
        return redirect(url_for('main.add_bookmark_manually', error=1))
    return render_template('register_bookmark.html', form=form,
                            categories=categories, path=path)

@main.route('/add_bookmark_manually/<error>',  methods=['GET', 'POST'])
@login_required
def add_bookmark_manually(error):
    grabzIt = GrabzItClient.GrabzItClient("OTU1ODEwNTVmZGU0NDMyNmE0NWRlZThkMDQ0NWViN2I=", "PD9VPz8/KD9VPyk/P0dNPyE/Pz8NPz8/Oz8IPxI/Lj8=")
    categories = get_categories()
    form = BookmarkFormManual()
    if form.validate_on_submit():
        url = form.link.data
        title = form.title.data
        description = form.title.data
        category_id = form.category.data
        user_id = current_user.id
        bookmark = Bookmark(link=url, title=title, description=description,
                            category_id=category_id, user_id=user_id)
        db.session.add(bookmark)
        db.session.commit()

        grabzIt.SetImageOptions(bookmark.link)
        directory = safe_join(os.path.join(current_app.config['UPLOAD_FOLDER']), "bookmarks")
        if not os.path.exists(directory):
            print("No existe")
            os.makedirs(directory)
        extension = '.jpg'
        picture_name = "%i%s" % (bookmark.id, extension)
        path_picture = safe_join(os.path.join(directory), picture_name)
        grabzIt.SaveTo(path_picture)

        return redirect(url_for('main.bookmarks', category_id=category_id))
    if error == '1':
        flash('We\'re sorry, but we couldn\'t save your bookmark automatically, please try it manually.')
    return render_template('register_bookmark_manually.html', form=form,
                            categories=categories)

@main.route('/search_bookmarks', methods=['GET', 'POST'])
@login_required
def search_bookmarks():
    search_string = "%" + request.args.get('search_string', '', type=str) + "%"
    category_id = request.args.get('category_id', 0, type=int)
    bookmarks = Bookmark.query.filter(Bookmark.title.ilike(search_string), Bookmark.category_id==category_id,
                                        Bookmark.user_id==current_user.id)
    resp = make_response(render_template('search_bookmarks.html', bookmarks=bookmarks, category_id=category_id))
    return resp

@main.route('/remove_bookmark', methods=['GET', 'POST'])
@login_required
def remove_bookmark():
    bookmark_id = request.args.get('bookmark_id', 0, type=int)
    category_id = request.args.get('category_id', 0, type=int)
    #search_string = "%%the%%"
    #category_id = 2
    bookmark = Bookmark.query.filter_by(id=bookmark_id).first()
    db.session.delete(bookmark)
    db.session.commit()
    bookmarks = get_bookmarks(category_id)
    resp = make_response(render_template('search_bookmarks.html', bookmarks=bookmarks, category_id=category_id))
    return resp

@main.route('/move_bookmark', methods=['GET', 'POST'])
@login_required
def move_bookmark():
    bookmark_id = request.args.get('bookmark_id', 0, type=int)
    category_id = request.args.get('category_id', 0, type=int)
    new_category_id = request.args.get('new_category_id', 0, type=int)
    bookmark = Bookmark.query.filter_by(id=bookmark_id).first()
    bookmark.category_id = new_category_id
    db.session.add(bookmark)
    db.session.commit()
    bookmarks = get_bookmarks(category_id)
    resp = make_response(render_template('search_bookmarks.html', bookmarks=bookmarks, category_id=category_id))
    return resp

@main.route('/edit_bookmark/<bookmark_id>',  methods=['GET', 'POST'])
@login_required
def edit_bookmark(bookmark_id):
    categories = get_categories()
    form = BookmarkFormManual()
    user_id = current_user.id
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    category_id = bookmark.category_id
    if form.validate_on_submit():
        bookmark.link = form.link.data
        bookmark.title = form.title.data
        bookmark.description = form.description.data
        bookmark.category_id = form.category.data
        db.session.add(bookmark)
        db.session.commit()

        return redirect(url_for('main.bookmarks', category_id=category_id))
    if bookmark:
        form.link.data = bookmark.link
        form.title.data = bookmark.title
        form.description.data = bookmark.description
        form.category.data = str(category_id)
    return render_template('edit_bookmark.html', form=form,
                            categories=categories)

@main.route('/uploads/<bookmark_id>')
def get_file(bookmark_id):
    extension = '.jpg'
    filename = "%s%s" % (bookmark_id, extension)
    filename = safe_join(os.path.join("bookmarks"), filename)
    upload_folder = safe_join(os.path.join(os.getcwd()), current_app.config['UPLOAD_FOLDER'])
    print(filename)
    return send_from_directory(upload_folder, filename)
