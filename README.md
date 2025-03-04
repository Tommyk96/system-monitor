# System Monitor Desktop Application

## Описание

Это приложение для мониторинга системных ресурсов (ЦП, ОЗУ, ПЗУ) в реальном времени на компьютере, на котором оно запущено. Программа отображает информацию о текущей загрузке системы с возможностью записи данных в базу данных, а также просмотра истории записей. Время обновления данных на экране можно настроить в пределах от 1 до 5 секунд.

## Требования

Для работы приложения необходимо:

- Python 3.6 или выше
- Библиотеки:
  - `psutil`
  - `PyQt5`
  - `psycopg2`
- База данных PostgreSQL

## Установка

1. Клонируйте репозиторий на ваш локальный компьютер:
   ```bash
   git clone https://github.com/yourusername/system-monitor.git
   cd system-monitor

2. Автоматическая установка библиотек:
   ```bash
   pip install -r requirements.txt

3. Настроить переменные окружения:
   Программа использует пароль для подключения к базе данных через переменную окружения DB_PASSWORD. Убедитесь, что вы установили эту переменную:
   ```bash
   export DB_PASSWORD="your_database_password"

4. Запустите приложения:
   ```bash
   python3 main.py


5. Для тестирования покрытия выполните команду:
   ```bash
   coverage run -m pytest
   pytest test.py
   pytest -vv --log-level=DEBUG test.py


6. Покрытие тестами: Установите необходимые пакеты для тестирования:
   ```bash
   Установите необходимые пакеты:
   pip install pytest coverage