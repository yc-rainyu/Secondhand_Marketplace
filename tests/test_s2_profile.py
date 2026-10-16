from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User, Product


def test_change_password(logged_in_client, app, seller):
    resp = logged_in_client.post(
        f'/dashboard/{seller}',
        data={
            'username': 'seller',
            'password': '11111111',
            'password_confirm': '11111111',
            'submit': 'Update profile',
        },
        follow_redirects=True,
    )
    assert b'Profile updated successfully' in resp.data

    with app.app_context():
        user = db.session.get(User, seller)
        assert check_password_hash(user.password, '11111111')

    logged_in_client.get('/logout', follow_redirects=True)
    bad = logged_in_client.post(
        '/login',
        data={'email': 'seller@test.com', 'password': 'password1'},
        follow_redirects=True,
    )
    assert b'Login Failed' in bad.data

    good = logged_in_client.post(
        '/login',
        data={'email': 'seller@test.com', 'password': '11111111'},
        follow_redirects=True,
    )
    assert b'Login Failed' not in good.data


def test_edit_product_price(logged_in_client, app, seller, catalog):
    with app.app_context():
        phone = Product(
            name='Phone',
            price=2999.99,
            category='digital',
            description='this is a phone',
            image='uploads/placeholder.png',
            user_id=seller,
        )
        db.session.add(phone)
        db.session.commit()
        product_id = phone.id

    resp = logged_in_client.post(
        f'/edit/{product_id}',
        data={
            'name': 'Phone',
            'category': 'digital',
            'description': 'this is a phone',
            'price': '99999999.0',
            'submit': 'Post',
        },
        follow_redirects=True,
    )
    assert b'Product updated successfully' in resp.data

    with app.app_context():
        assert db.session.get(Product, product_id).price == 99999999.0


def test_delete_product(logged_in_client, app, seller, catalog):
    with app.app_context():
        phone = Product(
            name='Phone',
            price=2999.99,
            category='digital',
            description='this is a phone',
            image='uploads/placeholder.png',
            user_id=seller,
        )
        db.session.add(phone)
        db.session.commit()
        product_id = phone.id

    resp = logged_in_client.post(f'/delete/{product_id}', follow_redirects=True)
    assert b'Product deleted successfully' in resp.data

    with app.app_context():
        assert db.session.get(Product, product_id) is None


def test_cannot_delete_others_product(client, app, catalog):
    with app.app_context():
        other = User(
            username='other',
            email='other@test.com',
            password=generate_password_hash('password1'),
        )
        db.session.add(other)
        db.session.commit()
        product_id = Product.query.filter_by(name='Whale').first().id

    client.post(
        '/login',
        data={'email': 'other@test.com', 'password': 'password1'},
        follow_redirects=True,
    )
    resp = client.post(f'/delete/{product_id}', follow_redirects=True)
    assert b'not authorized' in resp.data.lower()

    with app.app_context():
        assert db.session.get(Product, product_id) is not None
