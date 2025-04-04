import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

#Постгре
def get_db_connection():
    connection = psycopg2.connect(
        dbname="project_management",
        user="postgres",
        password="eg",
        host="localhost",  
        port="5432"       
    )
    return connection

def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    #Пользователи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            fullname TEXT NOT NULL,
            position TEXT NOT NULL,
            role TEXT NOT NULL
        );
    ''')

    #Статусы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statuses (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    ''')

    #Проекты
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );
    ''')
    
    #Задачи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status_id INTEGER REFERENCES statuses(id),
            specialist_id INTEGER REFERENCES users(id),
            project_id INTEGER REFERENCES projects(id)
        );
    ''')

    #Комментарии
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            task_id INTEGER REFERENCES tasks(id),
            user_id INTEGER REFERENCES users(id),
            comment TEXT NOT NULL
        );
    ''')

    # Добавление статусов по умолчанию
    statuses = ['открыта', 'в работе', 'решена', 'на согласовании']
    for status in statuses:
        cursor.execute("INSERT INTO statuses (name, active) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING", (status, True))

    # Добавление администратора по умолчанию
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('admin') 
        cursor.execute(
            "INSERT INTO users (login, password, fullname, position, role) VALUES (%s, %s, %s, %s, %s)",
            ('admin', hashed_password, 'Администратор', 'Руководитель', 'admin')
        )

    connection.commit()
    cursor.close()
    connection.close()