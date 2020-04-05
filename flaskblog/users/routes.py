# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import del_old_picture, save_picture, send_reset_email


users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Log-in failed! Check your credentials.', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        #inaczej blad, ze zajete - mozna rozdzielic per pole
        if form.username.data != current_user.username or form.email.data != current_user.email:
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('your account has been updated', 'success')
        if form.picture.data:
            del_old_picture(current_user.image_file)
            current_user.image_file = save_picture(form.picture.data)
            db.session.commit()
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Your details', image_file=image_file, form=form)


@users.route('/user/<string:user_name>')
def user_posts(user_name):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=user_name).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request(): 
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # weryfikacja istnienia emaila przez forms.RRF.validate_email
        try:
            send_reset_email(user)
            flash('A reset email was sent', 'info')
        except:
            flash('Could not send the reset email', 'warning')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token): 
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('The token is either invalid or expired', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset password', form=form)