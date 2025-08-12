import pytest
import json
import tempfile
import os
from datetime import date
from unittest.mock import patch
import sys
from io import StringIO

from main import parse_args, main, read_logs, generate_average_report


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

    # Очистка
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass


def test_parse_args_valid(log_file):

    """Тест валидных аргументов"""
    test_args = ['main.py', '--file', log_file, '--report', 'average']

    with patch.object(sys, 'argv', test_args):
        args = parse_args()
        assert args.file == [log_file]
        assert args.report == 'average'


def test_parse_args_multiple_files(log_file):

    """Тест нескольких файлов"""
    test_args = ['main.py', '--file', log_file, log_file, '--report', 'user_agents']

    with patch.object(sys, 'argv', test_args):
        args = parse_args()
        assert len(args.file) == 2
        assert args.report == 'user_agents'


def test_parse_args_with_date(log_file):
    """Тест аргументов с датой"""
    test_args = ['main.py', '--file', log_file, '--report', 'average', '--date', '2025-06-22']

    with patch.object(sys, 'argv', test_args):
        args = parse_args()
        assert args.date == '2025-06-22'


def test_parse_args_invalid_file():
    """Тест невалидного файла"""

    test_args = ['main.py', '--file', 'nonexistent.log', '--report', 'average']

    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            parse_args()


def test_parse_args_missing_required():
    """Тест отсутствующих обязательных аргументов"""

    test_args = ['main.py', '--file', 'test.log']

    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            parse_args()


def test_main_average_report(log_file):
    """Тест main функции с average отчетом"""

    test_args = ['main.py', '--file', log_file, '--report', 'average']

    # Перехватываем stdout
    captured_output = StringIO()
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', captured_output):
            main()

    output = captured_output.getvalue()
    assert 'endpoint' in output
    assert 'request_count' in output


def test_main_user_agents_report(log_file):
    """Тест main функции с user_agents отчетом"""

    test_args = ['main.py', '--file', log_file, '--report', 'user_agents']

    # Перехватываем stdout
    captured_output = StringIO()
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', captured_output):
            main()

    output = captured_output.getvalue()
    assert 'user_agent' in output
    assert 'count' in output


def test_main_invalid_date_format(log_file):
    """Тест main функции с невалидным форматом даты"""

    test_args = ['main.py', '--file', log_file, '--report', 'average', '--date', 'invalid-date']

    captured_output = StringIO()
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', captured_output):
            main()

    output = captured_output.getvalue()
    assert 'Неправильный формат даты' in output


def test_main_empty_data():
    """Тест main функции с пустыми данными"""

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    temp_file.close()

    test_args = ['main.py', '--file', temp_file.name, '--report', 'average']

    captured_output = StringIO()
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', captured_output):
            main()

    output = captured_output.getvalue()
    assert 'Нет данных для отображения' in output

    try:
        os.unlink(temp_file.name)
    except OSError:
        pass


def test_main_date_filtering(log_file):
    """Тест main функции с фильтрацией по дате"""

    test_args = ['main.py', '--file', log_file, '--report', 'average', '--date', '2025-06-21']

    captured_output = StringIO()
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', captured_output):
            main()

    output = captured_output.getvalue()
    assert 'Нет данных для отображения' in output


def test_integration_main_function(log_file):
    """Интеграционный тест для main функции"""

    test_args = ['main.py', '--file', log_file, '--report', 'average']

    # Перехватываем stdout
    captured_output = StringIO()
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', captured_output):
            main()

    output = captured_output.getvalue()

    assert len(output) > 0
    assert 'api/context' in output or 'api/homeworks' in output