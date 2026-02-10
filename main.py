# импортируем фреймворк и тип значений для дополнительного описания
from fastapi import FastAPI, Query

# создаём объект приложения FastAPI
app = FastAPI()

from typing import Optional
from pydantic import BaseModel


# создаём корневой эндпойнт, на который будут отправлять GET-запрос
@app.get('/')
# пишем асинхронную обработку запроса
async def home():
   # возвращаем информацию
   return {'Hello!': 'This is a test GET-request to the API'}

@app.get("/time")
def get_time():
    from datetime import datetime
    now = datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

# создаём класс-модель специально для обновлений книг
class UpdateBook(BaseModel):
   # переменная book будет строкой
   book: Optional[str] = None
   # переменная price будет вещественным числом
   price: Optional[float] = None
   # переменная author будет опциональной, строкового типа и по умолчанию равной None
   author: Optional[str] = None


# создаём класс-модель для добавления в наш общий словарь
class BookInfo(BaseModel):
   # переменная book будет строкой
   book: str
   # переменная price будет вещественным числом
   price: float
   # переменная author будет опциональной, строкового типа и по умолчанию равной None
   author: Optional[str] = None

bookshelf = {
       1: {
           'book': 'Ulyss',
           'price': 4.75,
           'author': 'James Joyce'
       },

       2: {
           'book': 'Three Men in a Boat (To Say Nothing of the Dog)',
           'price': 3.99,
           'author': 'Jerome K. Jerome'
       }
   }

# создаём POST-эндпойнт:
@app.post('/create-book/{book_id}')
# пишем асинхронную обработку запроса и указываем тип значений, который
# ждём от пользователя: целое число и словарь по шаблону BookInfo
async def create_book(book_id: int, new_book: BookInfo):
   # проверяем, что в словаре bookshelf ещё нет книги с таким номером
   if book_id in bookshelf:
       # выводим сообщение об ошибке, которое FastAPI трансформирует в JSON
       return {'Error': 'Book already exists'}

   # если книги с таким номером ещё нет, создаём её под этим номером
   # и с теми же параметрами, которые указали в классе BookInfo
   bookshelf[book_id] = new_book
   # возвращаем данные о новой внесённой книге
   return bookshelf[book_id]

@app.put('/update-book/{book_id}')
async def update_book(book_id: int, upd_book: UpdateBook):
    if book_id not in bookshelf:
        return {'Error': 'Книги с таким ID не существует'}
    
    book_data = bookshelf[book_id]
    if upd_book.book is not None:
        book_data['book'] = upd_book.book
    if upd_book.price is not None:
        book_data['price'] = upd_book.price
    if upd_book.author is not None:
        book_data['author'] = upd_book.author
    
    return book_data

# создаём ещё один GET-эндпойнт с проверкой типа и получением значения по ключу:
@app.get('/get-book/{book_id}')
# пишем асинхронную обработку запроса и указываем
# тип значения, который ждём от пользователя: целое число
async def get_book(book_id: int):
   # возвращаем информацию о книге с выбранным номером
   return bookshelf[book_id]

# создаём DELETE-эндпойнт:
@app.delete('/delete-book')
# пишем асинхронную обработку запроса и указываем тип значений, который
# ждём от пользователя: целое число. Добавляем описание
def delete_book(book_id: int = Query(..., description='The book ID must be greater than zero')):
   # если книги с таким номером нет, выводим сообщение об ошибке
   if book_id not in bookshelf:
       return {'Error': 'Book ID does not exists'}
   # если номер книги есть, удаляем о ней всю информацию, включая номер
   del bookshelf[book_id]
   return {'Done': 'The book successfully deleted'}

# Словарь с пользователями (ключ - строка)
users = {
    "alice": {"name": "Алиса", "age": 25, "city": "Москва"},
    "bob": {"name": "Боб", "age": 30, "city": "СПб"}
}

#  GET-эндпойнт
@app.get('/user/{username}')
def get_user(username: str):
    return users.get(username, {"error": "Пользователь не найден"})


# Модель для пользователя
class UserInfo(BaseModel):
    name: str
    age: int
    city: Optional[str] = None

# POST-запрос для добавления пользователя
@app.post('/add-user/{username}')
def add_user(username: str, user: UserInfo):
    if username in users:
        return {"error": "Пользователь уже существует"}
    
    users[username] = user.dict()
    return {"message": "Пользователь добавлен", "user": users[username]}

# Модель для обновления пользователя
class UpdateUser(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

# PUT-метод для обновления
@app.put("/update-user/{username}")
def update_user(username: str, user_update: UpdateUser):
    if username not in users:
        return {"error": "Пользователь не найден"}
    
    if user_update.name is not None:
        users[username]["name"] = user_update.name
    if user_update.age is not None:
        users[username]["age"] = user_update.age
    
    return {"message": "Обновлено", "user": users[username]}

# DELETE-метод для удаления пользователя
@app.delete("/delete-user/{username}")
def delete_user(username: str):
    """
    Удаляет пользователя по имени пользователя.
    
    - **username**: Имя пользователя для удаления
    - Возвращает сообщение об успешном удалении или ошибку
    """
    if username not in users:
        return {"error": "Пользователь не найден"}
    
    # Сохраняем информацию об удаляемом пользователе
    deleted_user = users[username].copy()
    
    # Удаляем пользователя из словаря
    del users[username]
    
    return {
        "message": "Пользователь успешно удален",
        "deleted_username": username,
        "deleted_user_info": deleted_user,
        "remaining_users": len(users)
    }
