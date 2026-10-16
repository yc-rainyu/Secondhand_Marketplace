import pytest
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash

from app import app as flask_app, db
from app.models import User, Product


def _use_db(uri):
    # Flask-SQLAlchemy caches engines; swap so tests don't touch instance/market.db
    db.session.remove()
    binds = db._app_engines[flask_app]
    old = binds.pop(None, None)
    if old is not None:
        old.dispose()
    binds[None] = create_engine(uri)


@pytest.fixture
def app(tmp_path):
    uploads = tmp_path / 'uploads'
    uploads.mkdir()
    uri = f'sqlite:///{tmp_path / "test.db"}'

    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY='test-key',
        SQLALCHEMY_DATABASE_URI=uri,
        UPLOAD_FOLDER=str(uploads),
    )

    with flask_app.app_context():
        _use_db(uri)
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
        eng = db._app_engines[flask_app].pop(None, None)
        if eng is not None:
            eng.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seller(app):
    with app.app_context():
        user = User(
            username='seller',
            email='seller@test.com',
            password=generate_password_hash('password1'),
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def logged_in_client(client, seller):
    client.post(
        '/login',
        data={'email': 'seller@test.com', 'password': 'password1'},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def catalog(app, seller):
    # sample catalogue used by search / filter tests (from manual test cases)
    items = [
        ('Whale', 9999.0, 'digital'),
        ('Aliens', 300.0, 'book'),
        ('Helicopter', 6.0, 'daily'),
        ('Little Pup', 954.0, 'book'),
        ('Disk', 473.0, 'book'),
        ('Others', 201.3, 'others'),
        ('charm', 70.0, 'daily'),
    ]
    with app.app_context():
        for name, price, category in items:
            db.session.add(Product(
                name=name,
                price=price,
                category=category,
                description=name,
                image='uploads/placeholder.png',
                user_id=seller,
            ))
        db.session.commit()
