# Log Parser

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск скрипта
python main.py --file example1.log --report average
<img width="746" height="190" alt="log1" src="https://github.com/user-attachments/assets/b6f5cb16-f8cc-46ea-989d-3cfab1a8fb40" />

# Запуск с несколькими файлами
python main.py --file example1.log example2.log --report average
<img width="881" height="201" alt="log2" src="https://github.com/user-attachments/assets/a4262d7e-4cda-41c4-9841-8c6feb1e6af1" />


# Запуск тестов
pytest tests/ -v

# Запуск тестов с coverage
pytest tests/ --cov=. --cov-report=term-missing
<img width="721" height="211" alt="coverage" src="https://github.com/user-attachments/assets/5fc45368-9c74-479a-8449-c03334c9601c" />
