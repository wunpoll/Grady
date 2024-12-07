import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('media/Grady.db')
cursor = conn.cursor()

# Таблица Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL
)
''')

# Таблица Teacher
cursor.execute('''
CREATE TABLE IF NOT EXISTS Teacher (
    user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_name VARCHAR(100),
    group_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(id),
    FOREIGN KEY(group_id) REFERENCES Groups (id)
)
''')

# Таблица Student
cursor.execute('''
CREATE TABLE IF NOT EXISTS Student (
    user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_name VARCHAR(100),
    group_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(id),
    FOREIGN KEY(group_id) REFERENCES Groups (id)
)
''')

# Таблица Group
cursor.execute('''
CREATE TABLE IF NOT EXISTS Groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL
)
''')

# Таблица Factors
cursor.execute('''
CREATE TABLE IF NOT EXISTS Factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    mother_education VARCHAR(100),
    father_education VARCHAR(100),
    free_time_hours INTEGER,
    additional_activities VARCHAR(100),
    olympiads_part VARCHAR(100),
    FOREIGN KEY(student_id) REFERENCES Student(user_id)
)
''')

# Таблица Grades
cursor.execute('''
CREATE TABLE IF NOT EXISTS Grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    predicted_grade FLOAT,
    FOREIGN KEY(student_id) REFERENCES Student(user_id)
)
''')

# Заполнение тестовыми данными

# Добавление пользователей
cursor.executemany('''
INSERT OR IGNORE INTO Users (email, password, role)
VALUES (?, ?, ?)
''', [
    ('admin', '1', 'administrator'),  # Администратор
    ('teacher1@gmail.com', '1', 'teacher'),  # Учитель
    ('student1@gmail.com', '1', 'student'),  # Студент
    ('student2@gmail.com', '1', 'student')
])

# Добавление групп
cursor.executemany('''
INSERT OR IGNORE INTO Groups (name, specialization)
VALUES (?, ?)
''', [
    ('Группа 1', 'Программирование'),
    ('Группа 2', 'Информационные системы')
])

# Добавление учителей
cursor.executemany('''
INSERT OR IGNORE INTO Teacher (user_id, first_name, last_name, middle_name, group_id)
VALUES (?, ?, ?, ?, ?)
''', [
    (2, 'Иван', 'Иванов', 'Иванович', 1)
])

# Добавление студентов
cursor.executemany('''
INSERT OR IGNORE INTO Student (user_id, first_name, last_name, middle_name, group_id)
VALUES (?, ?, ?, ?, ?)
''', [
    (3, 'Петр', 'Петров', 'Петрович', 1),
    (4, 'Мария', 'Иванова', 'Сергеевна', 1)
])

# Добавление факторов для студентов
cursor.executemany('''
INSERT OR IGNORE INTO Factors (student_id, mother_education, father_education, free_time_hours, additional_activities, olympiads_part)
VALUES (?, ?, ?, ?, ?, ?)
''', [
    (3, 'Высшее', 'Среднее', 2, 'Нет', 'Да'),
    (4, 'Среднее', 'Среднее', 4, 'Да', 'Нет')
])

# Добавление оценок для студентов
cursor.executemany('''
INSERT OR IGNORE INTO Grades (student_id, predicted_grade)
VALUES (?, ?)
''', [
    (3, 65.0),
    (4, 40)
])

conn.commit()
conn.close()

print("База данных успешно создана и заполнена!")
