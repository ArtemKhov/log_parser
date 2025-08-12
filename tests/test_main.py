import pytest
import json
import tempfile
import os
from main import read_logs, generate_average_report, generate_user_agents_report


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

    # Все 5 записей должны быть прочитаны успешно
    assert len(entries) == 5

    # Проверяем структуру записей
    for entry in entries:
        assert all(key in entry for key in ['@timestamp', 'url', 'response_time', 'http_user_agent'])
        assert isinstance(entry['response_time'], float)
        assert entry['status'] == 200


def test_generate_average_report():
    """Тест генерации average отчета"""
    entries = [
        {"url": "/api/context/...", "response_time": 0.024},
        {"url": "/api/context/...", "response_time": 0.02},
        {"url": "/api/context/...", "response_time": 0.024},
        {"url": "/api/homeworks/...", "response_time": 0.06},
        {"url": "/api/homeworks/...", "response_time": 0.032}
    ]

    report = generate_average_report(entries)

    # Должно быть 2 эндпоинта
    assert len(report) == 2


    context_data = next((item for item in report if item['endpoint'] == '/api/context/...'), None)
    homeworks_data = next((item for item in report if item['endpoint'] == '/api/homeworks/...'), None)

    # Проверяем /api/context/...
    assert context_data is not None
    assert context_data['request_count'] == 3
    # Проверяем, что среднее время в разумных пределах
    assert 0.022 <= context_data['average_response_time'] <= 0.023

    # Проверяем /api/homeworks/...
    assert homeworks_data is not None
    assert homeworks_data['request_count'] == 2
    assert abs(homeworks_data['average_response_time'] - 0.046) < 0.001

    # Проверяем сортировку
    assert report[0]['endpoint'] == '/api/context/...'
    assert report[1]['endpoint'] == '/api/homeworks/...'


def test_generate_user_agents_report():
    """Тест генерации user_agents отчета"""
    entries = [
        {"http_user_agent": "Mozilla"},
        {"http_user_agent": "Chrome"},
        {"http_user_agent": "Chrome"},
        {"http_user_agent": "Opera"},
        {"http_user_agent": "..."}
    ]

    report = generate_user_agents_report(entries)

    # Должно быть 4 уникальных user agent'а
    assert len(report) == 4

    ua_counts = {item['user_agent']: item['count'] for item in report}

    # Проверяем количество для каждого user agent'а (независимо от порядка)
    expected_counts = {
        "Chrome": 2,
        "Mozilla": 1,
        "Opera": 1,
        "...": 1
    }

    assert ua_counts == expected_counts


def test_average_calculation_precision():
    """Тест точности вычисления среднего времени ответа"""
    entries = [
        {"url": "/test", "response_time": 0.1},
        {"url": "/test", "response_time": 0.2},
        {"url": "/test", "response_time": 0.3}
    ]

    report = generate_average_report(entries)
    assert len(report) == 1
    assert report[0]['request_count'] == 3
    assert abs(report[0]['average_response_time'] - 0.2) < 0.001


def test_sorting_by_request_count():
    """Тест правильной сортировки по количеству запросов"""
    entries = []

    entries.extend([
        {"url": "/api/less_used", "response_time": 0.1},
        {"url": "/api/less_used", "response_time": 0.2}
    ])

    entries.extend([
        {"url": "/api/more_used", "response_time": 0.05},
        {"url": "/api/more_used", "response_time": 0.06},
        {"url": "/api/more_used", "response_time": 0.07},
        {"url": "/api/more_used", "response_time": 0.08}
    ])

    report = generate_average_report(entries)

    # Первым должен быть эндпоинт с большим количеством запросов
    assert len(report) == 2
    assert report[0]['endpoint'] == '/api/more_used'
    assert report[0]['request_count'] == 4
    assert report[1]['endpoint'] == '/api/less_used'
    assert report[1]['request_count'] == 2


def test_empty_data_handling():
    """Тест обработки пустых данных"""
    # Пустой отчет average
    report = generate_average_report([])
    assert report == []

    # Пустой отчет user_agents
    report = generate_user_agents_report([])
    assert report == []


def test_single_entry_data():
    """Тест с одной записью"""
    entries = [{"url": "/api/single", "response_time": 0.05, "http_user_agent": "Safari"}]

    # Тест average отчета
    avg_report = generate_average_report(entries)
    assert len(avg_report) == 1
    assert avg_report[0]['endpoint'] == '/api/single'
    assert avg_report[0]['request_count'] == 1
    assert abs(avg_report[0]['average_response_time'] - 0.05) < 0.001

    # Тест user_agents отчета
    ua_report = generate_user_agents_report(entries)
    assert len(ua_report) == 1
    assert ua_report[0]['user_agent'] == 'Safari'
    assert ua_report[0]['count'] == 1


def test_integration_data(log_file):
    """Интеграционный тест"""
    entries = read_logs([log_file])
    assert len(entries) == 5

    # Генерируем average отчет
    average_report = generate_average_report(entries)
    assert len(average_report) == 2

    # Проверяем структуру отчета
    for item in average_report:
        assert 'endpoint' in item
        assert 'request_count' in item
        assert 'average_response_time' in item
        assert isinstance(item['request_count'], int)
        assert isinstance(item['average_response_time'], float)

    # Генерируем user_agents отчет
    ua_report = generate_user_agents_report(entries)
    assert len(ua_report) == 4

    # Проверяем количество для каждого user agent'а
    ua_counts = {item['user_agent']: item['count'] for item in ua_report}
    assert ua_counts["Chrome"] == 2
    assert ua_counts["Mozilla"] == 1
    assert ua_counts["Opera"] == 1
    assert ua_counts["..."] == 1