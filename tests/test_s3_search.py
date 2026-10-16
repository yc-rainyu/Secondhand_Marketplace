def test_search_by_keyword(client, catalog):
    resp = client.get('/search?q=whale')
    assert b'Whale' in resp.data
    assert b'Aliens' not in resp.data


def test_filter_by_price_range(client, catalog):
    # d = 100 ~ 500
    resp = client.get('/search?price_range=d')
    assert b'Aliens' in resp.data
    assert b'Disk' in resp.data
    assert b'Others' in resp.data
    assert b'Whale' not in resp.data


def test_filter_by_category(client, catalog):
    resp = client.get('/market?category=book')
    assert b'Aliens' in resp.data
    assert b'Little Pup' in resp.data
    assert b'Disk' in resp.data
    assert b'Whale' not in resp.data
