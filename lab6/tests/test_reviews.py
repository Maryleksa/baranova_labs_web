import pytest
from app import create_app, db
from app.models import User, Course, Category, Review

@pytest.fixture
def app():
    app = create_app(test_config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        db.create_all()
        
        # Создаём тестового пользователя
        user = User(first_name='Test', last_name='User', login='testuser')
        user.set_password('Test123!')
        db.session.add(user)
        
        # Создаём категорию
        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()
        
        # Создаём курс
        course = Course(
            name='Test Course',
            short_desc='Test description',
            full_desc='Full test description',
            author_id=user.id,
            category_id=category.id,
            background_image_id=None
        )
        db.session.add(course)
        db.session.commit()
        
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_reviews_page_accessible(client):
    response = client.get('/courses/1/reviews')
    assert response.status_code == 200

def test_add_review_requires_login(client):
    response = client.post('/courses/1/review/create', data={
        'rating': 5,
        'text': 'Great course!'
    })
    assert response.status_code == 302  # Redirect to login

def test_add_review_authenticated(client):
    # Сначала логинимся
    client.post('/login', data={'login': 'testuser', 'password': 'Test123!'})
    
    response = client.post('/courses/1/review/create', data={
        'rating': 5,
        'text': 'Great course!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Отзыв успешно добавлен' in response.data

def test_cannot_add_duplicate_review(client):
    client.post('/login', data={'login': 'testuser', 'password': 'Test123!'})
    
    # Первый отзыв
    client.post('/courses/1/review/create', data={'rating': 5, 'text': 'First review'})
    
    # Второй отзыв (должен быть отклонён)
    response = client.post('/courses/1/review/create', data={'rating': 4, 'text': 'Second review'}, follow_redirects=True)
    assert b'Вы уже оставили отзыв' in response.data

def test_review_shows_on_course_page(client):
    client.post('/login', data={'login': 'testuser', 'password': 'Test123!'})
    client.post('/courses/1/review/create', data={'rating': 5, 'text': 'Great course!'})
    
    response = client.get('/courses/1')
    assert b'Great course!' in response.data

def test_review_sorting_newest(client):
    response = client.get('/courses/1/reviews?sort=newest')
    assert response.status_code == 200

def test_review_sorting_positive(client):
    response = client.get('/courses/1/reviews?sort=positive')
    assert response.status_code == 200

def test_review_sorting_negative(client):
    response = client.get('/courses/1/reviews?sort=negative')
    assert response.status_code == 200