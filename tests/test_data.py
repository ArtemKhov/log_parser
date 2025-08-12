import pytest
import json
import tempfile
import os
from datetime import date
from main import read_logs


@pytest.fixture
def log_data():
    """Набор тестовых данных"""
    return [
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
         "response_time": 0.024, "http_user_agent": "Mozilla"},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
         "response_time": 0.02, "http_user_agent": "Chrome"},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/context/...", "request_method": "GET",
         "response_time": 0.024, "http_user_agent": "Chrome"},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/homeworks/...", "request_method": "GET",
         "response_time": 0.06, "http_user_agent": "Opera"},
        {"@timestamp": "2025-06-22T13:57:32+00:00", "status": 200, "url": "/api/homeworks/...", "request_method": "GET",
         "response_time": 0.032, "http_user_agent": "..."}
    ]


@pytest.fixture
def log_file(log_data):
    """Создает временный файл с тестовыми данными"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    for entry in log_data:
        temp_file.write(json.dumps(entry) + '\n')
    temp_file.close()

    yield temp_file.name


def test_read_logs(log_file):
    """Тест чтения логов"""
    entries = read_logs([log_file])

    assert len(entries) == 5

    for entry in entries:
        assert all(key in entry for key in ['@timestamp', 'url', 'response_time', 'http_user_agent'])
        assert isinstance(entry['response_time'], (int, float))
        assert entry['status'] == 200


def test_read_logs_with_date_filter(log_file):
    """Тест чтения логов с фильтрацией по дате"""

    # Тестовые данные имеют дату 2025-06-22
    entries = read_logs([log_file], date_filter=date(2025, 6, 22))
    assert len(entries) == 5

    # Фильтрация по другой дате должна вернуть 0 записей
    entries = read_logs([log_file], date_filter=date(2025, 6, 21))
    assert len(entries) == 0


def test_read_logs_invalid_json():
    """Тест обработки некорректного JSON"""

    # Создаем файл с некорректным JSON
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    temp_file.write('{"valid": "json"}\n')
    temp_file.write('invalid json line\n')
    temp_file.write('{"another": "valid"}\n')
    temp_file.close()

    entries = read_logs([temp_file.name])
    assert len(entries) == 2  # Только валидные записи

    try:
        os.unlink(temp_file.name)
    except OSError:
        pass