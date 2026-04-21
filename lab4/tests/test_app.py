import pytest
from app import app, validate_login, validate_password
import models

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    models.init_db()
    with app.test_client() as client:
        with app.app_context():
            yield client

# ============ ТЕСТЫ СТРАНИЦ ============

def test_index_page_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_page_returns_200(client):
    response = client.get('/login/')
    assert response.status_code == 200

def test_successful_login_redirects(client):
    response = client.post('/login/', data={
        'login': 'admin',
        'password': 'Admin123!'
    }, follow_redirects=False)
    assert response.status_code == 302

def test_successful_login_redirects_to_index(client):
    response = client.post('/login/', data={
        'login': 'admin',
        'password': 'Admin123!'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_failed_login_stays_on_login_page(client):
    response = client.post('/login/', data={
        'login': 'admin',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    assert b'login' in response.data

# ============ ТЕСТЫ ВАЛИДАЦИИ ЛОГИНА ============

def test_validate_login_valid():
    is_valid, error = validate_login('user123')
    assert is_valid is True
    assert error is None

def test_validate_login_too_short():
    is_valid, error = validate_login('usr')
    assert is_valid is False
    assert error is not None

def test_validate_login_empty():
    is_valid, error = validate_login('')
    assert is_valid is False

def test_validate_login_invalid_chars():
    is_valid, error = validate_login('user_123')
    assert is_valid is False

def test_validate_login_only_letters():
    is_valid, error = validate_login('username')
    assert is_valid is True

def test_validate_login_only_numbers():
    is_valid, error = validate_login('12345')
    assert is_valid is True

# ============ ТЕСТЫ ВАЛИДАЦИИ ПАРОЛЯ ============

def test_validate_password_valid():
    is_valid, error = validate_password('Admin123!')
    assert is_valid is True

def test_validate_password_too_short():
    is_valid, error = validate_password('Abc1!')
    assert is_valid is False

def test_validate_password_too_long():
    long_pwd = 'A' * 130 + 'b1!'
    is_valid, error = validate_password(long_pwd)
    assert is_valid is False

def test_validate_password_no_uppercase():
    is_valid, error = validate_password('admin123!')
    assert is_valid is False

def test_validate_password_no_lowercase():
    is_valid, error = validate_password('ADMIN123!')
    assert is_valid is False

def test_validate_password_no_digit():
    is_valid, error = validate_password('AdminAdmin!')
    assert is_valid is False

def test_validate_password_with_space():
    is_valid, error = validate_password('Admin 123!')
    assert is_valid is False

# ============ ТЕСТЫ ДОСТУПА ============

def test_authenticated_user_can_access_create_page(client):
    client.post('/login/', data={'login': 'admin', 'password': 'Admin123!'})
    response = client.get('/user/create/')
    assert response.status_code == 200

def test_unauthenticated_user_redirected_from_create(client):
    response = client.get('/user/create/')
    assert response.status_code == 302

def test_user_view_page_accessible_to_all(client):
    response = client.get('/user/1/')
    assert response.status_code == 200

def test_user_view_shows_username(client):
    response = client.get('/user/1/')
    assert b'admin' in response.data

def test_change_password_page_requires_login(client):
    response = client.get('/change-password/')
    assert response.status_code == 302

def test_change_password_page_accessible_when_logged_in(client):
    client.post('/login/', data={'login': 'admin', 'password': 'Admin123!'})
    response = client.get('/change-password/')
    assert response.status_code == 200

# ============ ТЕСТЫ СМЕНЫ ПАРОЛЯ ============

def test_change_password_wrong_old_password(client):
    client.post('/login/', data={'login': 'admin', 'password': 'Admin123!'})
    response = client.post('/change-password/', data={
        'old_password': 'WrongPassword!',
        'new_password': 'NewPass456!',
        'confirm_password': 'NewPass456!'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_change_password_mismatch(client):
    client.post('/login/', data={'login': 'admin', 'password': 'Admin123!'})
    response = client.post('/change-password/', data={
        'old_password': 'Admin123!',
        'new_password': 'NewPass456!',
        'confirm_password': 'DifferentPass!'
    }, follow_redirects=True)
    assert response.status_code == 200

# ============ ТЕСТЫ CRUD ============

def test_create_user_page_loads(client):
    client.post('/login/', data={'login': 'admin', 'password': 'Admin123!'})
    response = client.get('/user/create/')
    assert response.status_code == 200
    assert b'form' in response.data

def test_logout_works(client):
    client.post('/login/', data={'login': 'admin', 'password': 'Admin123!'})
    response = client.get('/logout/', follow_redirects=True)
    assert response.status_code == 200