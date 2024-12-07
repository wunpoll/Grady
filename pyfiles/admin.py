import sys
import os
import random
import string
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QDialog,
    QRadioButton, QButtonGroup, QComboBox, QFileDialog, QHeaderView
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setGeometry(100, 100, 1000, 700)
        
        # Применяем темную тему
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #666666;
            }
            QTableWidget {
                background-color: #2d2d2d;
                border: none;
                gridline-color: #3d3d3d;
                selection-background-color: #007acc;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
                color: white;
            }
            QComboBox:drop-down {
                border: 0px;
            }
            QComboBox:down-arrow {
                image: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                selection-background-color: #007acc;
                selection-color: white;
            }
            QLineEdit {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QRadioButton::indicator:checked {
                background-color: #007acc;
                border: 2px solid white;
                border-radius: 7px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #3d3d3d;
                border: 2px solid white;
                border-radius: 7px;
            }
        """)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Верхняя панель с кнопками и фильтрами
        top_panel = QHBoxLayout()
        
        # Секция фильтров
        filter_group = QWidget()
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        self.role_filter = QComboBox()
        self.role_filter.addItems(["Все роли", "Администратор", "Учитель", "Ученик"])
        self.role_filter.currentTextChanged.connect(self.apply_filters)
        
        filter_layout.addWidget(QLabel("Фильтр:"))
        filter_layout.addWidget(self.role_filter)
        filter_layout.addStretch()

        # Секция кнопок
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        import_button = QPushButton("Импорт из Excel")
        import_button.clicked.connect(self.import_from_excel)
        
        self.button_add_user = QPushButton("Добавить пользователя")
        self.button_add_user.clicked.connect(self.add_user_window)
        self.button_add_group = QPushButton("Добавить группу")
        self.button_add_group.clicked.connect(self.add_group_window)
        
        button_layout.addWidget(import_button)
        button_layout.addWidget(self.button_add_user)
        button_layout.addWidget(self.button_add_group)

        top_panel.addWidget(filter_group)
        top_panel.addWidget(button_group)
        self.layout.addLayout(top_panel)

        # Таблицы
        self.table_users = QTableWidget()
        self.table_groups = QTableWidget()

        # Настройка таблицы пользователей
        self.table_users.setColumnCount(3)
        self.table_users.setHorizontalHeaderLabels(["ID", "Email", "Роль"])
        self.table_users.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_users.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_users.horizontalHeader().sectionClicked.connect(self.sort_table)

        # Настройка таблицы групп
        self.table_groups.setColumnCount(4)
        self.table_groups.setHorizontalHeaderLabels(["ID", "Название", "Специализация", "Учитель"])
        self.table_groups.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_groups.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_groups.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Добавление заголовков секций
        users_label = QLabel("Пользователи:")
        users_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        groups_label = QLabel("Группы:")
        groups_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")

        self.layout.addWidget(users_label)
        self.layout.addWidget(self.table_users)
        self.layout.addWidget(groups_label)
        self.layout.addWidget(self.table_groups)

        # Загрузка данных
        self.load_data()

        # Подключение сигналов
        self.table_groups.cellDoubleClicked.connect(self.edit_group)
        self.table_users.cellDoubleClicked.connect(self.edit_user)
        self.table_users.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_groups.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)


    def sort_table(self, column):
        if column == 2:  # Колонка "Роль"
            # Сохраняем текущий порядок сортировки
            if not hasattr(self, 'sort_order'):
                self.sort_order = Qt.SortOrder.AscendingOrder
            else:
                self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder

            # Определяем порядок сортировки ролей
            role_order = {
                'administrator': 0,
                'teacher': 1,
                'student': 2
            }

            # Получаем все строки из таблицы
            items = []
            for row in range(self.table_users.rowCount()):
                items.append([
                    self.table_users.item(row, 0).text(),  # ID
                    self.table_users.item(row, 1).text(),  # Email
                    self.table_users.item(row, 2).text(),  # Role
                    row  # Сохраняем оригинальную позицию
                ])

            # Сортируем
            items.sort(
                key=lambda x: role_order.get(x[2].lower(), 999),
                reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
            )

            # Обновляем таблицу
            for new_row, item in enumerate(items):
                for col in range(3):  # Только первые три колонки
                    self.table_users.item(item[3], col).setText(item[col])

    def generate_password(self):
            characters = string.ascii_letters + string.digits
            password = ''.join(random.choice(characters) for _ in range(8))
            return password

    def send_email(self, to_email, password):
        smtp_server = "smtp.yandex.ru"
        smtp_port = 465
        from_email = "v4nya.poletaev@yandex.ru"
        from_password = "nzgfaimafitnuiri"

        subject = "Данные для входа в Grady"
        body = f"Здравствуйте!\n\nВаши данные для входа:\nЛогин: {to_email}\nПароль: {password}\n\nС уважением, Grady!"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        print(body)
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(from_email, from_password)
                server.send_message(msg)
            print("Письмо отправлено!")
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")


    def import_from_excel(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите Excel файл",
                "",
                "Excel Files (*.xlsx *.xls)"
            )
            
            if not file_name:
                return

            # Читаем Excel файл
            df = pd.read_excel(file_name)
            
            # Проверяем наличие необходимых колонок
            required_columns = ['email', 'role', 'first_name', 'last_name', 'middle_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
                )
                return

            # Подключаемся к базе данных
            db_path = resource_path("media/Grady.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Начинаем транзакцию
            cursor.execute("BEGIN TRANSACTION")

            try:
                for _, row in df.iterrows():
                    password = self.generate_password()
                    cursor.execute(
                        "INSERT INTO Users (email, password, role) VALUES (?, ?, ?)",
                        (row['email'], password, row['role'].lower())
                    )
                    user_id = cursor.lastrowid
                    self.send_email(row['email'], password)
                    # В зависимости от роли добавляем дополнительную информацию
                    if row['role'].lower() == 'student':
                        cursor.execute(
                            """INSERT INTO Student 
                               (user_id, first_name, last_name, middle_name, group_id)
                               VALUES (?, ?, ?, ?, NULL)""",
                            (user_id, row['first_name'], row['last_name'], row['middle_name'])
                        )
                    elif row['role'].lower() == 'teacher':
                        cursor.execute(
                            """INSERT INTO Teacher 
                               (user_id, first_name, last_name, middle_name, group_id)
                               VALUES (?, ?, ?, ?, NULL)""",
                            (user_id, row['first_name'], row['last_name'], row['middle_name'])
                        )
                    
                cursor.execute("COMMIT")
                QMessageBox.information(
                    self,
                    "Успех",
                    "Данные успешно импортированы!"
                )
                self.apply_filters()  # Обновляем таблицу

            except Exception as e:
                cursor.execute("ROLLBACK")
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Ошибка при импорте данных: {str(e)}"
                )
            finally:
                conn.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при чтении файла: {str(e)}"
            )

    def load_data(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Загрузка пользователей
        selected_role = self.role_filter.currentText()
        if selected_role == "Все роли":
            cursor.execute("""
                SELECT u.id, u.email, u.role 
                FROM Users u
                ORDER BY 
                    CASE u.role 
                        WHEN 'administrator' THEN 1
                        WHEN 'teacher' THEN 2
                        WHEN 'student' THEN 3
                    END
            """)
        else:
            role = selected_role.lower()
            cursor.execute("""
                SELECT u.id, u.email, u.role 
                FROM Users u
                WHERE LOWER(u.role) = ?
                ORDER BY u.email
            """, (role,))

        users = cursor.fetchall()
        self.table_users.setRowCount(len(users))
        
        for row_index, (id, email, role) in enumerate(users):
            self.table_users.setItem(row_index, 0, QTableWidgetItem(str(id)))
            self.table_users.setItem(row_index, 1, QTableWidgetItem(email))
            self.table_users.setItem(row_index, 2, QTableWidgetItem(role))

        # Загрузка групп остается без изменений
        cursor.execute("""
            SELECT g.id, g.name, g.specialization, 
                COALESCE(t.first_name || ' ' || t.last_name, 'Нет учителя') AS teacher
            FROM Groups g
            LEFT JOIN Teacher t ON g.id = t.group_id
        """)
        groups = cursor.fetchall()
        self.table_groups.setRowCount(len(groups))
        
        for row_index, (id, name, specialization, teacher) in enumerate(groups):
            self.table_groups.setItem(row_index, 0, QTableWidgetItem(str(id)))
            self.table_groups.setItem(row_index, 1, QTableWidgetItem(name))
            self.table_groups.setItem(row_index, 2, QTableWidgetItem(specialization))
            self.table_groups.setItem(row_index, 3, QTableWidgetItem(teacher))

        conn.close()
    
    def add_user_window(self):
        dialog = AddUserDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.apply_filters()

    def add_group_window(self):
        dialog = AddGroupDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.apply_filters()

    def edit_group(self, row, column):
        """Открывает окно для редактирования группы."""
        group_id = self.table_groups.item(row, 0).text()
        group_name = self.table_groups.item(row, 1).text()
        specialization = self.table_groups.item(row, 2).text()
        teacher = self.table_groups.item(row, 3).text() if self.table_groups.item(row, 3) else ""

        # Открываем диалоговое окно редактирования группы
        edit_group_dialog = EditGroupDialog(group_id, group_name, specialization, teacher)
        if edit_group_dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.apply_filters()
            

    def edit_user(self, row, column):
        user_id = self.table_users.item(row, 0).text()
        role = self.table_users.item(row, 2).text().lower()

        dialog = EditUserDialog(user_id, role)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self.apply_filters()

    def apply_filters(self):
        role_mapping = {
        "Администратор": "administrator",
        "Учитель": "teacher",
        "Ученик": "student"
    }
        selected_role = self.role_filter.currentText()
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if selected_role == "Все роли":
            cursor.execute("SELECT id, email, role FROM Users")
        else:
            selected_role = role_mapping[selected_role]
            role = selected_role.lower()
            cursor.execute("SELECT id, email, role FROM Users WHERE LOWER(role) = ?", (role,))

        users = cursor.fetchall()
        self.table_users.setRowCount(len(users))
        
        for row_index, (id, email, role) in enumerate(users):
            self.table_users.setItem(row_index, 0, QTableWidgetItem(str(id)))
            self.table_users.setItem(row_index, 1, QTableWidgetItem(email))
            self.table_users.setItem(row_index, 2, QTableWidgetItem(role))

        conn.close()


class AddUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить пользователя")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
                font-size: 13px;
                margin-top: 10px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: white;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QRadioButton {
                color: white;
                spacing: 5px;
                margin: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                background-color: #007acc;
                border: 2px solid white;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #3d3d3d;
                border: 2px solid white;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Email
        self.label_email = QLabel("Email:")
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email")
        layout.addWidget(self.label_email)
        layout.addWidget(self.input_email)

        # Password section
        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Введите пароль")
        
        btn_generate = QPushButton("Сгенерировать")
        btn_generate.setFixedWidth(140)
        btn_generate.clicked.connect(self.generate_password)
        
        self.btn_show = QPushButton()
        self.btn_show.setIcon(QIcon("media/closed.png"))
        self.btn_show.setFixedWidth(40)
        self.btn_show.setCheckable(True)
        self.btn_show.clicked.connect(self.toggle_password_visibility)

        password_layout.addWidget(self.input_password)
        password_layout.addWidget(btn_generate)
        password_layout.addWidget(self.btn_show)

        self.label_password = QLabel("Пароль:")
        layout.addWidget(self.label_password)
        layout.addWidget(password_widget)

        # Role section
        role_label = QLabel("Роль:")
        layout.addWidget(role_label)

        role_widget = QWidget()
        role_layout = QHBoxLayout(role_widget)
        role_layout.setContentsMargins(0, 0, 0, 0)

        self.radio_student = QRadioButton("Ученик")
        self.radio_teacher = QRadioButton("Учитель")
        self.radio_admin = QRadioButton("Администратор")
        self.radio_student.setChecked(True)

        self.role_group = QButtonGroup(self)
        self.role_group.addButton(self.radio_student)
        self.role_group.addButton(self.radio_teacher)
        self.role_group.addButton(self.radio_admin)

        role_layout.addWidget(self.radio_student)
        role_layout.addWidget(self.radio_teacher)
        role_layout.addWidget(self.radio_admin)
        layout.addWidget(role_widget)

        # Personal info section
        self.personal_info_widget = QWidget()
        personal_layout = QVBoxLayout(self.personal_info_widget)
        personal_layout.setContentsMargins(0, 0, 0, 0)

        # ФИО
        self.label_last_name = QLabel("Фамилия:")
        self.input_last_name = QLineEdit()
        self.input_last_name.setPlaceholderText("Введите фамилию")
        
        self.label_first_name = QLabel("Имя:")
        self.input_first_name = QLineEdit()
        self.input_first_name.setPlaceholderText("Введите имя")
        
        self.label_middle_name = QLabel("Отчество:")
        self.input_middle_name = QLineEdit()
        self.input_middle_name.setPlaceholderText("Введите отчество")

        personal_layout.addWidget(self.label_last_name)
        personal_layout.addWidget(self.input_last_name)
        personal_layout.addWidget(self.label_first_name)
        personal_layout.addWidget(self.input_first_name)
        personal_layout.addWidget(self.label_middle_name)
        personal_layout.addWidget(self.input_middle_name)

        layout.addWidget(self.personal_info_widget)

        # Group selection (for students)
        self.group_widget = QWidget()
        group_layout = QVBoxLayout(self.group_widget)
        group_layout.setContentsMargins(0, 0, 0, 0)

        self.label_group = QLabel("Группа:")
        self.combo_group = QComboBox()
        self.combo_group.addItem("Без группы", -1)
        
        group_layout.addWidget(self.label_group)
        group_layout.addWidget(self.combo_group)
        
        layout.addWidget(self.group_widget)

        # Save button
        self.button_save = QPushButton("Сохранить")
        self.button_save.clicked.connect(self.add_user)
        layout.addWidget(self.button_save)

        self.setLayout(layout)
        
        # Connect signals
        self.role_group.buttonClicked.connect(self.update_fields)
        
        # Load groups
        self.load_groups()
        
        # Initial update
        self.update_fields()

    def load_groups(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Groups")
        groups = cursor.fetchall()
        for group_id, group_name in groups:
            self.combo_group.addItem(group_name, group_id)
        conn.close()

    def generate_password(self):
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(8))
        self.input_password.setText(password)

    def send_email(self, to_email, password):
        smtp_server = "smtp.yandex.ru"
        smtp_port = 465
        from_email = "v4nya.poletaev@yandex.ru"
        from_password = "nzgfaimafitnuiri"

        subject = "Данные для входа в Grady"
        body = f"Здравствуйте!\n\nВаши данные для входа:\nЛогин: {to_email}\nПароль: {password}\n\nС уважением, Grady!"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        print(body)
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(from_email, from_password)
                server.send_message(msg)
            print("Письмо отправлено!")
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")

    def toggle_password_visibility(self):
        if self.input_password.echoMode() == QLineEdit.EchoMode.Password:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_show.setIcon(QIcon("media/open.png"))
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_show.setIcon(QIcon("media/closed.png"))

    def update_fields(self):
        role = self.role_group.checkedButton().text().lower()
        self.personal_info_widget.setVisible(role in ['ученик', 'учитель'])
        self.group_widget.setVisible(role == 'ученик')

    def add_user(self):
        try:
            email = self.input_email.text().strip()
            password = self.input_password.text().strip()
            role = self.role_group.checkedButton().text().lower()
            
            if not email or not password:
                raise ValueError("Email и пароль обязательны для заполнения")

            db_path = resource_path("media/Grady.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Начинаем транзакцию
            cursor.execute("BEGIN TRANSACTION")
            
            # Проверяем существование email внутри транзакции
            cursor.execute("SELECT id FROM Users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise ValueError("Пользователь с таким email уже существует")

            if role == 'ученик':
                role = 'student'
            elif role == 'учитель':
                role = 'teacher'
            else:
                role = 'administrator'

            # Добавляем пользователя
            cursor.execute(
                "INSERT INTO Users (email, password, role) VALUES (?, ?, ?)",
                (email, password, role)
            )
            user_id = cursor.lastrowid

            # Добавляем дополнительную информацию в зависимости от роли
            if role in ['student', 'teacher']:
                first_name = self.input_first_name.text().strip()
                last_name = self.input_last_name.text().strip()
                middle_name = self.input_middle_name.text().strip()

                if not all([first_name, last_name, middle_name]):
                    raise ValueError("Все поля ФИО обязательны для заполнения")

                if role == 'student':
                    group_id = self.combo_group.currentData()
                    cursor.execute(
                        """INSERT INTO Student 
                           (user_id, first_name, last_name, middle_name, group_id)
                           VALUES (?, ?, ?, ?, ?)""",
                        (user_id, first_name, last_name, middle_name, 
                         None if group_id == -1 else group_id)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO Teacher 
                           (user_id, first_name, last_name, middle_name)
                           VALUES (?, ?, ?, ?)""",
                        (user_id, first_name, last_name, middle_name)
                    )

            cursor.execute("COMMIT")
            QMessageBox.information(self, "Успех", "Пользователь успешно добавлен! \nПисьмо с данными для входа отправлено на указанный email.")
            self.send_email(email, password)
            self.accept()

        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

class EditUserDialog(QDialog):
    def __init__(self, user_id, role):
        super().__init__()
        self.setWindowTitle(f"Редактирование пользователя")
        self.setGeometry(100, 100, 400, 500)
        self.user_id = user_id
        self.role = role
        
        # Применяем тот же стиль, что и в AddUserDialog
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
                font-size: 13px;
                margin-top: 10px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: white;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        
        # Email
        self.label_email = QLabel("Email:")
        self.input_email = QLineEdit()
        layout.addWidget(self.label_email)
        layout.addWidget(self.input_email)


        if role in ['student', 'teacher']:
            self.label_first_name = QLabel("Имя:")
            self.input_first_name = QLineEdit()
            self.label_last_name = QLabel("Фамилия:")
            self.input_last_name = QLineEdit()
            self.label_middle_name = QLabel("Отчество:")
            self.input_middle_name = QLineEdit()

            layout.addWidget(self.label_last_name)
            layout.addWidget(self.input_last_name)
            layout.addWidget(self.label_first_name)
            layout.addWidget(self.input_first_name)
            layout.addWidget(self.label_middle_name)
            layout.addWidget(self.input_middle_name)

            if role == 'student':
                self.label_group = QLabel("Группа:")
                self.combo_group = QComboBox()
                self.combo_group.addItem("Без группы", -1)
                layout.addWidget(self.label_group)
                layout.addWidget(self.combo_group)
                self.load_groups()

        button_layout = QHBoxLayout()
        
        self.button_save = QPushButton("Сохранить")
        self.button_save.clicked.connect(self.save_changes)
        
        self.button_delete = QPushButton("Удалить")
        self.button_delete.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        self.button_delete.clicked.connect(self.delete_user)
        
        button_layout.addWidget(self.button_save)
        button_layout.addWidget(self.button_delete)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_user_data()

    def load_groups(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Groups")
        groups = cursor.fetchall()
        for group_id, group_name in groups:
            self.combo_group.addItem(group_name, group_id)
        conn.close()

    def load_user_data(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Loading data for user_id: {self.user_id}, role: {self.role}")  # Отладочный принт

        # Загружаем email
        cursor.execute("SELECT email FROM Users WHERE id = ?", (self.user_id,))
        user_data = cursor.fetchone()
        print(f"Email data: {user_data}")  # Отладочный принт

        if user_data:
            self.input_email.setText(user_data[0])

        # Загружаем дополнительные данные в зависимости от роли
        if self.role == 'student':
            cursor.execute("""
                SELECT first_name, last_name, middle_name, group_id
                FROM Student
                WHERE user_id = ?
            """, (self.user_id,))
            data = cursor.fetchone()
            print(f"Student data: {data}")  # Отладочный принт
            
            if data:
                self.input_first_name.setText(data[0])
                self.input_last_name.setText(data[1])
                self.input_middle_name.setText(data[2])
                index = self.combo_group.findData(data[3] if data[3] is not None else -1)
                if index >= 0:
                    self.combo_group.setCurrentIndex(index)

        elif self.role == 'teacher':
            cursor.execute("""
                SELECT first_name, last_name, middle_name
                FROM Teacher
                WHERE user_id = ?
            """, (self.user_id,))
            data = cursor.fetchone()
            print(f"Teacher data: {data}")  # Отладочный принт
            
            if data:
                self.input_first_name.setText(data[0])
                self.input_last_name.setText(data[1])
                self.input_middle_name.setText(data[2])

        conn.close()
    def delete_user(self):
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите удалить этого пользователя?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_path = resource_path("media/Grady.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("BEGIN TRANSACTION")
                
                # Удаляем связанные записи в зависимости от роли
                if self.role == 'student':
                    cursor.execute("DELETE FROM Student WHERE user_id = ?", (self.user_id,))
                elif self.role == 'teacher':
                    cursor.execute("DELETE FROM Teacher WHERE user_id = ?", (self.user_id,))
                
                # Удаляем пользователя
                cursor.execute("DELETE FROM Users WHERE id = ?", (self.user_id,))
                
                cursor.execute("COMMIT")
                QMessageBox.information(self, "Успех", "Пользователь успешно удален")
                self.accept()
            
            except Exception as e:
                cursor.execute("ROLLBACK")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
            
            finally:
                conn.close()

    def save_changes(self):
        try:
            email = self.input_email.text().strip()
            if not email:
                raise ValueError("Email обязателен для заполнения")

            db_path = resource_path("media/Grady.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("BEGIN TRANSACTION")

            # Обновляем email
            cursor.execute("UPDATE Users SET email = ? WHERE id = ?", 
                         (email, self.user_id))

            # Обновляем дополнительные данные
            if self.role == 'student':
                first_name = self.input_first_name.text().strip()
                last_name = self.input_last_name.text().strip()
                middle_name = self.input_middle_name.text().strip()
                group_id = self.combo_group.currentData()

                if not all([first_name, last_name, middle_name]):
                    raise ValueError("Все поля ФИО обязательны для заполнения")

                cursor.execute("""
                    UPDATE Student 
                    SET first_name = ?, last_name = ?, middle_name = ?, 
                        group_id = ?
                    WHERE user_id = ?
                """, (first_name, last_name, middle_name, 
                      None if group_id == -1 else group_id, self.user_id))

            elif self.role == 'teacher':
                first_name = self.input_first_name.text().strip()
                last_name = self.input_last_name.text().strip()
                middle_name = self.input_middle_name.text().strip()

                if not all([first_name, last_name, middle_name]):
                    raise ValueError("Все поля ФИО обязательны для заполнения")

                cursor.execute("""
                    UPDATE Teacher 
                    SET first_name = ?, last_name = ?, middle_name = ?
                    WHERE user_id = ?
                """, (first_name, last_name, middle_name, self.user_id))

            cursor.execute("COMMIT")
            QMessageBox.information(self, "Успех", "Данные успешно обновлены!")
            self.accept()

        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

class AddGroupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление группы")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
                font-size: 13px;
                margin-top: 10px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: white;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Название группы
        self.label_group_name = QLabel("Название группы:")
        self.input_group_name = QLineEdit()
        self.input_group_name.setPlaceholderText("Введите название группы")
        layout.addWidget(self.label_group_name)
        layout.addWidget(self.input_group_name)

        # Специализация
        self.label_specialization = QLabel("Специализация:")
        self.input_specialization = QLineEdit()
        self.input_specialization.setPlaceholderText("Введите специализацию")
        layout.addWidget(self.label_specialization)
        layout.addWidget(self.input_specialization)

        # Учитель
        self.label_teacher = QLabel("Учитель:")
        self.combo_teacher = QComboBox()
        self.combo_teacher.addItem("Без учителя", -1)
        layout.addWidget(self.label_teacher)
        layout.addWidget(self.combo_teacher)

        # Кнопка добавления
        self.button_add = QPushButton("Добавить группу")
        self.button_add.clicked.connect(self.add_group)
        layout.addWidget(self.button_add)

        self.setLayout(layout)
        self.load_teachers()

    def load_teachers(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Загружаем только свободных учителей
        cursor.execute("""
            SELECT user_id, first_name || ' ' || last_name as full_name
            FROM Teacher 
            WHERE group_id IS NULL
        """)
        teachers = cursor.fetchall()
        for teacher_id, teacher_name in teachers:
            self.combo_teacher.addItem(teacher_name, teacher_id)
        conn.close()

    def add_group(self):
        try:
            name = self.input_group_name.text().strip()
            specialization = self.input_specialization.text().strip()
            teacher_id = self.combo_teacher.currentData()

            if not name or not specialization:
                raise ValueError("Название и специализация обязательны для заполнения")

            db_path = resource_path("media/Grady.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("BEGIN TRANSACTION")

            # Добавляем группу
            cursor.execute(
                "INSERT INTO Groups (name, specialization) VALUES (?, ?)",
                (name, specialization)
            )
            group_id = cursor.lastrowid

            # Назначаем учителя, если выбран
            if teacher_id != -1:
                cursor.execute(
                    "UPDATE Teacher SET group_id = ? WHERE user_id = ?",
                    (group_id, teacher_id)
                )

            cursor.execute("COMMIT")
            QMessageBox.information(self, "Успех", "Группа успешно добавлена!")
            self.accept()

        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'conn' in locals():
                conn.close()


class EditGroupDialog(QDialog):
    def __init__(self, group_id, group_name, specialization, current_teacher):
        super().__init__()
        self.setWindowTitle(f"Редактирование группы {group_name}")
        self.setGeometry(100, 100, 400, 300)
        self.group_id = group_id

        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
                font-size: 13px;
                margin-top: 10px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: white;
                min-height: 25px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton#deleteButton {
                background-color: #dc3545;
            }
            QPushButton#deleteButton:hover {
                background-color: #c82333;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Название группы
        self.label_group_name = QLabel("Название группы:")
        self.input_group_name = QLineEdit(group_name)
        layout.addWidget(self.label_group_name)
        layout.addWidget(self.input_group_name)

        # Специализация
        self.label_specialization = QLabel("Специализация:")
        self.input_specialization = QLineEdit(specialization)
        layout.addWidget(self.label_specialization)
        layout.addWidget(self.input_specialization)

        # Учитель
        self.label_teacher = QLabel("Учитель:")
        self.combo_teacher = QComboBox()
        self.combo_teacher.addItem("Без учителя", -1)
        layout.addWidget(self.label_teacher)
        layout.addWidget(self.combo_teacher)

        # Кнопки
        button_layout = QHBoxLayout()
        
        self.button_save = QPushButton("Сохранить изменения")
        self.button_save.clicked.connect(self.save_changes)
        
        self.button_delete = QPushButton("Удалить группу")
        self.button_delete.setObjectName("deleteButton")
        self.button_delete.clicked.connect(self.delete_group)
        
        button_layout.addWidget(self.button_save)
        button_layout.addWidget(self.button_delete)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_teachers(current_teacher)

    def load_teachers(self, current_teacher):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Загружаем свободных учителей и текущего учителя группы
        cursor.execute("""
            SELECT user_id, first_name || ' ' || last_name as full_name
            FROM Teacher 
            WHERE group_id IS NULL OR group_id = ?
        """, (self.group_id,))
        teachers = cursor.fetchall()
        for teacher_id, teacher_name in teachers:
            self.combo_teacher.addItem(teacher_name, teacher_id)
            if teacher_name == current_teacher:
                self.combo_teacher.setCurrentIndex(self.combo_teacher.count() - 1)
        conn.close()

    def save_changes(self):
        try:
            name = self.input_group_name.text().strip()
            specialization = self.input_specialization.text().strip()
            new_teacher_id = self.combo_teacher.currentData()

            if not name or not specialization:
                raise ValueError("Название и специализация обязательны для заполнения")

            db_path = resource_path("media/Grady.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("BEGIN TRANSACTION")

            # Обновляем информацию о группе
            cursor.execute("""
                UPDATE Groups 
                SET name = ?, specialization = ?
                WHERE id = ?
            """, (name, specialization, self.group_id))

            # Сначала убираем привязку текущего учителя
            cursor.execute("""
                UPDATE Teacher 
                SET group_id = NULL 
                WHERE group_id = ?
            """, (self.group_id,))

            # Назначаем нового учителя, если выбран
            if new_teacher_id != -1:
                cursor.execute("""
                    UPDATE Teacher 
                    SET group_id = ? 
                    WHERE user_id = ?
                """, (self.group_id, new_teacher_id))

            cursor.execute("COMMIT")
            QMessageBox.information(self, "Успех", "Изменения успешно сохранены!")
            self.accept()

        except Exception as e:
            if 'cursor' in locals():
                cursor.execute("ROLLBACK")
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_group(self):
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите удалить эту группу?\nВсе ученики будут отвязаны от группы.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_path = resource_path("media/Grady.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("BEGIN TRANSACTION")

                # Отвязываем учителя
                cursor.execute("""
                    UPDATE Teacher 
                    SET group_id = NULL 
                    WHERE group_id = ?
                """, (self.group_id,))

                cursor.execute("""
                    UPDATE Student 
                    SET group_id = NULL 
                    WHERE group_id = ?
                """, (self.group_id,))

                # Удаляем группу
                cursor.execute("DELETE FROM Groups WHERE id = ?", (self.group_id,))

                cursor.execute("COMMIT")
                QMessageBox.information(self, "Успех", "Группа успешно удалена!")
                self.accept()

            except Exception as e:
                if 'cursor' in locals():
                    cursor.execute("ROLLBACK")
                QMessageBox.critical(self, "Ошибка", str(e))
            finally:
                if 'conn' in locals():
                    conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    admin_window = AdminWindow()
    admin_window.show()
    sys.exit(app.exec())

