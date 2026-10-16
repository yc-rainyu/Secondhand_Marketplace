from app.models import Product
from tests.helpers import png_file


def test_upload_product_appears_on_market(logged_in_client, app, catalog):
    resp = logged_in_client.post(
        '/upload',
        data={
            'name': 'Phone',
            'category': 'digital',
            'description': 'this is a phone',
            'price': '2999.99',
            'image': png_file('photo.png'),
            'submit': 'Post',
        },
        content_type='multipart/form-data',
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert b'Phone' in resp.data

    with app.app_context():
        phone = Product.query.filter_by(name='Phone').one()
        assert phone.price == 2999.99
        assert phone.category == 'digital'


def test_upload_requires_login(client):
    resp = client.get('/upload', follow_redirects=True)
    assert b'Login' in resp.data
