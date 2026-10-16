import os
import time
import random

from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app import app, db
from app.models import User, Product
from app.forms import ProductForm, RegisterForm, LoginForm, ProfileForm, PriceForm


@app.context_processor
def inject_price_form():
    return dict(price_form=PriceForm())


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


def save_product_image(image):
    """Save upload under static/uploads; return relative path or None if bad type."""
    _, ext = os.path.splitext(secure_filename(image.filename or ''))
    ext = ext.lower()
    if ext not in app.config['ALLOWED_EXTENSIONS']:
        return None

    filename = f'{int(time.time() * 1000)}_{random.randint(1000, 9999)}{ext}'
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return f'uploads/{filename}'


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = ProductForm()
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to access this site.', 'warning')
        return redirect(url_for('login'))

    if form.validate_on_submit():
        if not form.image.data:
            flash('New products must have a photo!', 'danger')
            return render_template(
                'upload.html', form=form, user=get_current_user(),
                is_edit=False, product=None,
            )

        image_path = save_product_image(form.image.data)
        if not image_path:
            flash('Only jpg, jpeg, and png images are allowed.', 'danger')
            return render_template(
                'upload.html', form=form, user=get_current_user(),
                is_edit=False, product=None,
            )

        db.session.add(Product(
            name=form.name.data,
            price=float(form.price.data),
            category=form.category.data,
            description=form.description.data,
            image=image_path,
            user_id=user_id,
        ))
        db.session.commit()
        return redirect(url_for('market'))

    return render_template('upload.html', form=form, user=get_current_user())


@app.route('/')
@app.route('/market')
def market():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    return render_template(
        'market.html',
        products=products,
        user=get_current_user(),
        current_category=category,
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'warning')
            return redirect(url_for('register'))
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'warning')
            return redirect(url_for('register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('market'))

    return render_template('register.html', form=form, user=get_current_user())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            return redirect(url_for('market'))
        flash('Login Failed', 'danger')
    return render_template('login.html', form=form, user=get_current_user())


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have logged out!', 'danger')
    return redirect(url_for('market'))


@app.route('/dashboard/<int:userid>', methods=['GET', 'POST'])
def dashboard(userid):
    form = ProfileForm()
    dashboard_user = db.session.get(User, userid)
    if not dashboard_user:
        flash('User not found.', 'danger')
        return redirect(url_for('market'))

    current_user = get_current_user()
    is_owner = current_user and current_user.id == dashboard_user.id

    if is_owner and form.validate_on_submit():
        new_username = form.username.data.strip()
        taken = User.query.filter(
            User.username == new_username,
            User.id != dashboard_user.id,
        ).first()
        if taken:
            flash('This username has already been taken.', 'warning')
            return redirect(url_for('dashboard', userid=userid))

        dashboard_user.username = new_username
        if form.password.data:
            dashboard_user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('dashboard', userid=userid))

    if is_owner and not form.username.data:
        form.username.data = dashboard_user.username

    return render_template(
        'dashboard.html',
        dashboard_user=dashboard_user,
        user=current_user,
        user_products=Product.query.filter_by(user_id=dashboard_user.id).all(),
        form=form if is_owner else None,
    )


@app.route('/product/<int:product_id>')
def product(product_id):
    target = db.session.get(Product, product_id)
    if not target:
        flash('Product not found.', 'danger')
        return redirect(url_for('market'))

    return render_template(
        'product.html',
        product=target,
        seller=target.owner,
        user=get_current_user(),
    )


@app.route('/search')
def search():
    keyword = request.args.get('q', '').strip()
    price_range = request.args.get('price_range', 'all')
    query = Product.query

    if keyword:
        query = query.filter(Product.name.ilike(f'%{keyword}%'))

    if price_range == 'a':
        query = query.filter(Product.price <= 10)
    elif price_range == 'b':
        query = query.filter(Product.price > 10, Product.price <= 50)
    elif price_range == 'c':
        query = query.filter(Product.price > 50, Product.price <= 100)
    elif price_range == 'd':
        query = query.filter(Product.price > 100, Product.price <= 500)
    elif price_range == 'e':
        query = query.filter(Product.price > 500, Product.price <= 1000)
    elif price_range == 'others':
        query = query.filter(Product.price > 1000)

    return render_template(
        'market.html',
        products=query.all(),
        keyword=keyword,
        user=get_current_user(),
        current_category=None,
    )


@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    target = Product.query.get_or_404(product_id)
    current_user = get_current_user()

    if not current_user:
        flash('Please login to access this site.', 'warning')
        return redirect(url_for('login'))
    if target.user_id != current_user.id:
        flash('You are not authorized to edit this product.', 'danger')
        return redirect(url_for('market'))

    form = ProductForm(obj=target)
    if form.validate_on_submit():
        target.name = form.name.data
        target.price = float(form.price.data)
        target.category = form.category.data
        target.description = form.description.data

        if form.image.data and isinstance(form.image.data, FileStorage) and form.image.data.filename:
            image_path = save_product_image(form.image.data)
            if not image_path:
                flash('Only jpg, jpeg, and png images are allowed.', 'danger')
                return render_template(
                    'upload.html', form=form, user=current_user,
                    product=target, is_edit=True, product_id=product_id,
                )
            target.image = image_path

        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('dashboard', userid=current_user.id))

    return render_template(
        'upload.html',
        form=form,
        user=current_user,
        product=target,
        is_edit=True,
        product_id=product_id,
    )


@app.route('/delete/<int:product_id>', methods=['POST'])
def delete(product_id):
    current_user = get_current_user()
    if not current_user:
        flash('Please login to access this site.', 'warning')
        return redirect(url_for('login'))

    target = Product.query.get_or_404(product_id)
    if target.user_id != current_user.id:
        flash('You are not authorized to delete this product.', 'danger')
        return redirect(url_for('market'))

    owner_id = target.user_id
    db.session.delete(target)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('dashboard', userid=owner_id))
