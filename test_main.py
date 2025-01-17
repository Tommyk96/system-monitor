import pytest
import os
import psycopg2
from PyQt5.QtWidgets import QApplication

import sys
sys.path.append('/home/fantomas/systemcp')
from main import SystemMonitor, connect_db



# Фикстура для настройки приложения и окна PyQt
@pytest.fixture(scope="module")
def app():
    app = QApplication([])
    yield app
    app.quit()  # Завершаем приложение после тестов


@pytest.fixture
def system_monitor(app):
    monitor = None
    try:
        monitor = SystemMonitor()
        yield monitor
    finally:
        if monitor and hasattr(monitor, "db_connection"):
            monitor.db_connection.close()


# Тест подключения к базе данных
def test_connect_db():
    connection = None
    try:
        connection = connect_db()
        assert connection is not None, "Подключение к базе данных не установлено"
    finally:
        if connection:
            connection.close()

# Тест создания таблицы в базе данных
def test_create_table(system_monitor):
    cursor = system_monitor.db_connection.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'system_data'
        );
    """)
    result = cursor.fetchone()
    assert result[0] is True, "Таблица system_data не была создана"

# Тест записи данных в базу данных
def test_write_to_db(system_monitor):
    try:
        cpu = 10.0
        ram = 20.0
        disk = 30.0
        
        system_monitor.write_to_db(cpu, ram, disk)

        cursor = system_monitor.db_connection.cursor()
        cursor.execute("""
            SELECT * FROM system_data ORDER BY id DESC LIMIT 1;
        """)
        row = cursor.fetchone()

        assert row is not None, "Запись не была добавлена в базу данных"
        assert row[2] == cpu, "Некорректное значение CPU в базе данных"
        assert row[3] == ram, "Некорректное значение RAM в базе данных"
        assert row[4] == disk, "Некорректное значение Disk в базе данных"
    except Exception as e:
        pytest.fail(f"Ошибка теста записи в базу данных: {e}")

# Тест выборки данных из базы данных
def test_fetch_data_from_db(system_monitor):
    try:
        system_monitor.db_cursor.execute("SELECT * FROM system_data ORDER BY id DESC LIMIT 10;")
        rows = system_monitor.db_cursor.fetchall()

        assert rows is not None, "Не удалось извлечь данные из базы данных"
        assert len(rows) > 0, "В базе данных отсутствуют записи"
    except Exception as e:
        pytest.fail(f"Ошибка теста выборки данных из базы данных: {e}")

# Тест изменения интервала обновления
def test_change_interval(system_monitor):
    initial_interval = system_monitor.update_interval
    system_monitor.interval_combo.setCurrentIndex(2)  # Устанавливаем интервал на 3 секунды

    assert system_monitor.update_interval == 3, "Интервал обновления не изменился"
    system_monitor.interval_combo.setCurrentIndex(0)  # Возвращаем исходный интервал
    assert system_monitor.update_interval == initial_interval, "Интервал обновления не восстановился"

# Тест кнопки Start Recording
def test_start_recording(system_monitor):
    system_monitor.start_recording()
    assert system_monitor.is_recording is True, "Запись не началась"
    system_monitor.stop_recording()
    assert system_monitor.is_recording is False, "Запись не остановилась"

if __name__ == "__main__":
    # Используем QCoreApplication для тестов без графического интерфейса
    from PyQt5.QtCore import QCoreApplication
    app = QCoreApplication([])
    monitor = SystemMonitor()
    print("SystemMonitor initialized successfully")
    app.quit()



