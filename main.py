import sys
import time
import psutil
import psycopg2
import logging
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QTextEdit
)
from PyQt5.QtCore import QTimer, QTime


# Настроим логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Подключение к PostgreSQL
def connect_db():
    try:
        logging.info("Connecting to PostgreSQL...")
        connection = psycopg2.connect(
            dbname="system_data",  # Имя базы данных
            user="admin_user",     # Имя пользователя
            password=os.getenv("DB_PASSWORD"),  # Пароль из переменной окружения
            host="localhost",      # Хост (локально)
            port="5432"            # Порт PostgreSQL
        )
        logging.info("Connection successful.")
        return connection
    except Exception as e:
        logging.error(f"Ошибка подключения к PostgreSQL: {e}")
        sys.exit(1)

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.recording_start_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.db_connection = connect_db()  # Подключение к базе данных
        self.db_cursor = self.db_connection.cursor()  # Создание курсора
        self.init_ui()

        # Создание таблицы, если её нет
        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_data (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpu_usage REAL,
            ram_usage REAL,
            disk_usage REAL
        );
        """)
        self.db_connection.commit()

    def init_ui(self):
        self.setWindowTitle("System Monitor")
        self.resize(300, 300)

        # Метки для отображения системной информации
        self.cpu_label = QLabel("CPU: 0.0%")
        self.ram_label = QLabel("RAM: 0.0%")
        self.disk_label = QLabel("Disk: 0.0%")
        self.recording_time_label = QLabel("Recording Time: 00:00")

        # Поле для задания интервала обновления
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1", "2", "3", "4", "5"])
        self.interval_combo_label = QLabel("Update Interval (s):")
        self.interval_combo.currentIndexChanged.connect(self.change_interval)

        # Кнопки управления
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setVisible(False)

        # Кнопка для отображения данных из базы
        self.show_data_button = QPushButton("Show Data")
        self.show_data_button.clicked.connect(self.fetch_data_from_db)

        # Текстовое поле для отображения данных из базы
        self.data_text_area = QTextEdit()
        self.data_text_area.setReadOnly(True)

        # Размещение элементов в окне
        layout = QVBoxLayout()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.recording_time_label)
        layout.addWidget(self.interval_combo_label)
        layout.addWidget(self.interval_combo)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.show_data_button)
        layout.addWidget(self.data_text_area)
        self.setLayout(layout)

        self.update_interval = 1
        self.timer.start(self.update_interval * 1000)  # Запуск таймера после его инициализации

    def update_stats(self):
        # Получение данных о загрузке системы
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        # Обновление меток
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        self.ram_label.setText(f"RAM: {ram:.1f}%")
        self.disk_label.setText(f"Disk: {disk:.1f}%")

        # Вывод данных в терминал с использованием logging
        logging.info(f"Current stats -> CPU: {cpu:.1f}%, RAM: {ram:.1f}%, Disk: {disk:.1f}%")

        # Если идет запись, сохраняем данные в базу
        if self.is_recording:
            self.write_to_db(cpu, ram, disk)
            elapsed_time = int(time.time() - self.recording_start_time)
            self.recording_time_label.setText(f"Recording Time: {QTime(0, 0).addSecs(elapsed_time).toString()}")

    def change_interval(self):
        # Изменение интервала обновления
        self.update_interval = int(self.interval_combo.currentText())
        self.timer.setInterval(self.update_interval * 1000)

    def start_recording(self):
        # Начало записи данных
        self.is_recording = True
        self.recording_start_time = time.time()
        self.start_button.setVisible(False)
        self.stop_button.setVisible(True)
        QMessageBox.information(self, "Recording started", "System monitoring data will now be recorded in the database.")
        logging.info("Recording started")

    def stop_recording(self):
        # Остановка записи данных
        self.is_recording = False
        self.recording_start_time = None
        self.start_button.setVisible(True)
        self.stop_button.setVisible(False)
        self.recording_time_label.setText("Recording Time: 00:00")
        QMessageBox.information(self, "Recording stopped", "System monitoring data recording has stopped.")
        logging.info("Recording stopped")

    def write_to_db(self, cpu, ram, disk):
        # Запись данных в базу данных
        try:
            logging.info(f"Writing to database -> CPU: {cpu:.1f}%, RAM: {ram:.1f}%, Disk: {disk:.1f}%")
            
            self.db_cursor.execute("""
            INSERT INTO system_data (cpu_usage, ram_usage, disk_usage)
            VALUES (%s, %s, %s);
            """, (cpu, ram, disk))

            self.db_connection.commit()

            logging.info("Data successfully written to database.")
        except Exception as e:
            logging.error(f"Ошибка записи в базу данных: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to write to the database: {e}")

    def fetch_data_from_db(self):
        # Извлечение данных из базы данных
        try:
            # Очистка текстового поля перед загрузкой новых данных
            self.data_text_area.clear()

            self.db_cursor.execute("SELECT * FROM system_data ORDER BY timestamp DESC LIMIT 10;")
            rows = self.db_cursor.fetchall()

            if not rows:
                self.data_text_area.setText("No data available.")
                logging.info("No data found in the database.")
                return

            data_text = ""
            for row in rows:
                data_text += f"ID: {row[0]} | CPU: {row[2]}% | RAM: {row[3]}% | Disk: {row[4]}% | Time: {row[1]}\n"
            
            self.data_text_area.setText(data_text)
            logging.info("Data successfully fetched from database.")
        
        except Exception as e:
            logging.error(f"Ошибка извлечения данных из базы: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to fetch data from the database: {e}")


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())

