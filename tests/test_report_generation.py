import pytest
from main import generate_average_report, generate_user_agents_report


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


def test_generate_user_agents_report_sorting():
    """Тест сортировки user agents по количеству"""
    entries = [
        {"http_user_agent": "MostUsed"},
        {"http_user_agent": "MostUsed"},
        {"http_user_agent": "MostUsed"},
        {"http_user_agent": "LessUsed"},
        {"http_user_agent": "LessUsed"},
    ]

    report = generate_user_agents_report(entries)

    # Первым должен быть MostUsed (3 запроса), потом LessUsed (2 запроса)
    assert len(report) == 2
    assert report[0]['user_agent'] == 'MostUsed'
    assert report[0]['count'] == 3
    assert report[1]['user_agent'] == 'LessUsed'
    assert report[1]['count'] == 2


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