import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                            QPushButton, QMessageBox, QWidget, QVBoxLayout)
from PyQt6.QtCore import Qt
import sqlite3
import os
from admin import AdminWindow


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'media/', relative_path)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: #ffffff;
                min-width: 200px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 30px;
                min-width: 200px;
                margin: 15px 0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton:focus {
                border: 2px solid #ffffff;
            }
        """)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        # Email
        self.label_email = QLabel("Email:")
        layout.addWidget(self.label_email)
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email")
        layout.addWidget(self.input_email)

        # Пароль
        self.label_password = QLabel("Пароль:")
        layout.addWidget(self.label_password)
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input_password)

        # Кнопка входа
        self.button_login = QPushButton("Войти")
        self.button_login.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Делаем доступным через Tab
        self.button_login.clicked.connect(self.login)
        layout.addWidget(self.button_login)

        # Устанавливаем порядок перехода по Tab
        self.input_email.setTabOrder(self.input_email, self.input_password)
        self.input_password.setTabOrder(self.input_password, self.button_login)

        # Позволяем нажать Enter для входа
        self.input_password.returnPressed.connect(self.button_login.click)
        self.input_email.returnPressed.connect(lambda: self.input_password.setFocus())


    def login(self):
        email = self.input_email.text()
        password = self.input_password.text()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        db_path = resource_path("Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM Users WHERE email = ? AND password = ?", (email, password))
        result = cursor.fetchone()

        if result:
            role = result[0]
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {role}!")

            if role == "administrator":
                self.open_admin_window()
            elif role == "teacher":
                cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
                teacher_id = cursor.fetchone()[0]
                self.open_teacher_window(teacher_id)
            elif role == "student":
                cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
                student_id = cursor.fetchone()[0]
                self.open_student_window(student_id)
            else:
                QMessageBox.warning(self, "Ошибка", "Эта роль пока не поддерживается для входа.")
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные логин или пароль!")

        conn.close()

    def open_admin_window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()
        self.close()  # Закрыть окно авторизации

    def open_teacher_window(self, teacher_id):
        from teacher import TeacherWindow
        self.teacher_window = TeacherWindow(teacher_id)
        self.teacher_window.show()
        self.close()

    def open_student_window(self, student_id):
        from student import StudentWindow
        self.student_window = StudentWindow(student_id)
        self.student_window.show()
        self.close()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())

