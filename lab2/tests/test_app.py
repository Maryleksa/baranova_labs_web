import pytest
from app import app, validate_phone

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ============ Тесты для страницы параметров URL ============
def test_url_params_no_params(client):
    response = client.get('/url-params/')
    assert response.status_code == 200
    assert b'Нет переданных параметров' in response.data

def test_url_params_with_params(client):
    response = client.get('/url-params/?param1=test&param2=hello&param3=world')
    assert response.status_code == 200
    assert b'test' in response.data
    assert b'hello' in response.data
    assert b'world' in response.data

def test_url_params_all_params_displayed(client):
    response = client.get('/url-params/?a=1&b=2&c=3')
    assert response.status_code == 200
    assert b'a' in response.data
    assert b'1' in response.data
    assert b'b' in response.data
    assert b'2' in response.data

# ============ Тесты для страницы заголовков ============
def test_headers_page_returns_200(client):
    response = client.get('/headers/')
    assert response.status_code == 200

def test_headers_display_host_header(client):
    response = client.get('/headers/')
    assert b'Host' in response.data

def test_headers_display_user_agent(client):
    response = client.get('/headers/')
    assert b'User-Agent' in response.data

# ============ Тесты для страницы Cookie ============
def test_cookie_not_set_initially(client):
    response = client.get('/cookies/')
    assert response.status_code == 200
    assert b'Cookie не установлено' in response.data

def test_set_cookie(client):
    response = client.get('/set-cookie/')
    assert 'lab_cookie' in response.headers.get('Set-Cookie', '')

def test_delete_cookie(client):
    response = client.get('/delete-cookie/')
    assert 'lab_cookie' in response.headers.get('Set-Cookie', '')

def test_cookie_display_when_set(client):
    client.get('/set-cookie/')
    response = client.get('/cookies/')
    assert response.status_code == 200

# ============ Тесты для страницы параметров формы ============
def test_form_params_get(client):
    response = client.get('/form-params/')
    assert response.status_code == 200
    assert b'Данные ещё не отправлены' in response.data

def test_form_params_post(client):
    data = {'name': 'Test User', 'email': 'test@example.com', 'message': 'Hello'}
    response = client.post('/form-params/', data=data)
    assert response.status_code == 200
    assert b'Test User' in response.data
    assert b'test@example.com' in response.data
    assert b'Hello' in response.data

# ============ Тесты для валидации телефона ============
def test_validate_phone_plus7_format():
    is_valid, error, formatted = validate_phone('+7 (123) 456-75-90')
    assert is_valid is True
    assert error is None
    assert formatted == '8-123-456-75-90'

def test_validate_phone_8_format():
    is_valid, error, formatted = validate_phone('8(123)4567590')
    assert is_valid is True
    assert error is None
    assert formatted == '8-123-456-75-90'

def test_validate_phone_10_digits():
    is_valid, error, formatted = validate_phone('123.456.75.90')
    assert is_valid is True
    assert error is None
    assert formatted == '123-456-75-90'

def test_validate_phone_simple_10_digits():
    is_valid, error, formatted = validate_phone('1234567590')
    assert is_valid is True
    assert error is None
    assert formatted == '123-456-75-90'

def test_validate_phone_invalid_chars():
    is_valid, error, formatted = validate_phone('123abc456')
    assert is_valid is False
    assert error == 'invalid_chars'

def test_validate_phone_wrong_digit_count_plus7():
    is_valid, error, formatted = validate_phone('+7 (123) 456-75')
    assert is_valid is False
    assert error == 'digit_count'

def test_validate_phone_wrong_digit_count_10_digits():
    is_valid, error, formatted = validate_phone('123456789')
    assert is_valid is False
    assert error == 'digit_count'

def test_phone_page_valid_submission(client):
    response = client.post('/phone/', data={'phone': '+7 (123) 456-75-90'})
    assert response.status_code == 200
    assert b'8-123-456-75-90' in response.data

def test_phone_page_invalid_chars(client):
    response = client.post('/phone/', data={'phone': '123abc456'})
    assert response.status_code == 200
    assert b'недопустимые символы' in response.data.lower()

def test_phone_page_invalid_digit_count(client):
    response = client.post('/phone/', data={'phone': '+7 (123) 456'})
    assert response.status_code == 200
    assert b'неверное количество цифр' in response.data.lower()

def test_phone_page_bootstrap_invalid_class(client):
    response = client.post('/phone/', data={'phone': 'invalid'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data

# ============ Дополнительные тесты ============
def test_index_page_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200

def test_all_pages_exist(client):
    pages = ['/', '/url-params/', '/headers/', '/cookies/', '/form-params/', '/phone/']
    for page in pages:
        response = client.get(page)
        assert response.status_code == 200, f'Page {page} failed'