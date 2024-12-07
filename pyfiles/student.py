from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QComboBox, QSpinBox,
                            QFormLayout, QFrame)
from PyQt6.QtCore import Qt
import sqlite3
import sys
import os

def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

class StudentWindow(QMainWindow):
    def __init__(self, student_id):
        super().__init__()
        self.student_id = student_id
        self.setWindowTitle("Личный кабинет ученика")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #ffffff;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Информация о студенте
        self.student_info = QLabel()
        self.student_info.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                background-color: #2d2d2d;
                border-radius: 8px;
                margin-bottom: 15px;
                color: #ffffff;
            }
        """)
        self.layout.addWidget(self.student_info)

        # Форма факторов
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                font-size: 13px;
                color: #ffffff;
            }
            QComboBox, QSpinBox {
                padding: 8px;
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                min-height: 25px;
                min-width: 200px;
                color: #ffffff;
            }
            QComboBox:drop-down {
                border: 0px;
            }
            QComboBox:down-arrow {
                image: none;
                border-width: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                color: #ffffff;
                selection-background-color: #4d4d4d;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4d4d4d;
                border-radius: 2px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)

        # Образование матери
        self.mother_edu = QComboBox()
        self.mother_edu.addItems(['Высшее', 'Среднее специальное', 'Среднее'])
        form_layout.addRow("Образование матери:", self.mother_edu)

        # Образование отца
        self.father_edu = QComboBox()
        self.father_edu.addItems(['Высшее', 'Среднее специальное', 'Среднее'])
        form_layout.addRow("Образование отца:", self.father_edu)

        # Свободное время
        self.free_time = QSpinBox()
        self.free_time.setRange(0, 12)
        form_layout.addRow("Свободное время (часов):", self.free_time)

        # Дополнительные занятия
        self.additional = QComboBox()
        self.additional.addItems(['Да', 'Нет'])
        form_layout.addRow("Дополнительные занятия:", self.additional)

        # Олимпиады
        self.olympiads = QComboBox()
        self.olympiads.addItems(['Да', 'Нет'])
        form_layout.addRow("Участие в олимпиадах:", self.olympiads)

        self.layout.addWidget(form_frame)

       # Кнопка сохранения
        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 30px;
                margin: 15px 0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)
        print("Создаем кнопку")  # Проверка создания кнопки
        self.save_button.clicked.connect(self.save_factors)
        print("Подключили обработчик")  # Проверка подключения обработчика
        self.layout.addWidget(self.save_button)

        # Загружаем данные
        self.load_student_info()
        self.load_factors()

    def load_student_info(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT Student.last_name, Student.first_name, Student.middle_name,
                   Groups.name as group_name
            FROM Student
            JOIN Groups ON Student.group_id = Groups.id
            WHERE Student.user_id = ?
        """, (self.student_id,))
        
        student_data = cursor.fetchone()
        if student_data:
            self.student_info.setText(
                f"{student_data[0]} {student_data[1]} {student_data[2]}\n"
                f"Группа: {student_data[3]}"
            )
        
        conn.close()

    def load_factors(self):
        db_path = resource_path("media/Grady.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mother_education, father_education, free_time_hours,
                   additional_activities, olympiads_part
            FROM Factors
            WHERE student_id = ?
        """, (self.student_id,))
        
        factors = cursor.fetchone()
        
        if factors:
            self.mother_edu.setCurrentText(factors[0])
            self.father_edu.setCurrentText(factors[1])
            self.free_time.setValue(factors[2])
            self.additional.setCurrentText(factors[3])
            self.olympiads.setCurrentText(factors[4])
        
        conn.close()

    def calculate_kpi(self, factors):
        kpi = 0
        
        education_levels = {
            'Высшее': 20,
            'Среднее специальное': 7,
            'Среднее': 5
        }
        kpi += education_levels.get(factors[0], 0)
        kpi += education_levels.get(factors[1], 0)
        
        free_time = factors[2]
        if free_time >= 4: kpi += 15
        elif free_time >= 2: kpi += 10
        else: kpi += 10
        
        if factors[3] == 'Да': kpi += 15
        if factors[4] == 'Да': kpi += 30
        
        return kpi

    def save_factors(self):
        try:
            print("Начало сохранения")
            
            factors = (
                self.mother_edu.currentText(),
                self.father_edu.currentText(),
                self.free_time.value(),
                self.additional.currentText(),
                self.olympiads.currentText()
            )
            
            print("Факторы собраны:", factors)
            kpi = self.calculate_kpi(factors)
            print("KPI посчитан:", kpi)
            
            db_path = resource_path("media/Grady.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Сначала проверим, существует ли запись
            cursor.execute("""
                SELECT COUNT(*) FROM Factors WHERE student_id = ?
            """, (self.student_id,))
            
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Обновляем существующую запись
                cursor.execute("""
                    UPDATE Factors 
                    SET mother_education = ?,
                        father_education = ?,
                        free_time_hours = ?,
                        additional_activities = ?,
                        olympiads_part = ?
                    WHERE student_id = ?
                """, (*factors, self.student_id))
            else:
                # Создаем новую запись
                cursor.execute("""
                    INSERT INTO Factors 
                    (mother_education, father_education, free_time_hours,
                    additional_activities, olympiads_part, student_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (*factors, self.student_id))

            print("Факторы сохранены")

            # Обновляем оценку
            cursor.execute("""
                SELECT COUNT(*) FROM Grades WHERE student_id = ?
            """, (self.student_id,))
            
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                cursor.execute("""
                    UPDATE Grades 
                    SET predicted_grade = ?
                    WHERE student_id = ?
                """, (kpi, self.student_id))
            else:
                cursor.execute("""
                    INSERT INTO Grades (student_id, predicted_grade)
                    VALUES (?, ?)
                """, (self.student_id, kpi))

            print("Оценка сохранена")
            
            conn.commit()  # Сохраняем изменения
            conn.close()

            print("Изменения зафиксированы в базе")
            QMessageBox.information(self, "Успех", "Факторы успешно сохранены!")
            
        except Exception as e:
            print("Ошибка:", str(e))
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить факторы: {str(e)}")

