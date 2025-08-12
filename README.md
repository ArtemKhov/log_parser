# Log Parser

Скрипт для анализа лог-файлов и генерации отчетов о производительности API.

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск скрипта
python main.py --file example1.log --report average

# Запуск с несколькими файлами
python main.py --file example1.log example2.log --report average

# Запуск тестов
pytest tests/ -v

# Запуск тестов с coverage
pytest tests/ --cov=. --cov-report=term-missing