import argparse
import json
from collections import defaultdict
from datetime import datetime

from tabulate import tabulate


def parse_args():
    parser = argparse.ArgumentParser(description='Обработка лог-файлов и формирование отчетов')
    parser.add_argument('--file', nargs='+', required=True, help='Путь до лог-файла(ов)')
    parser.add_argument('--report', choices=['average', 'user_agents'], required=True, help='Тип отчета')
    parser.add_argument('--date', help='Фильтрация лога по дате (YYYY-MM-DD)')
    args = parser.parse_args()

    # Проверка существования файлов
    for file_path in args.file:
        try:
            with open(file_path, 'r'):
                pass
        except IOError:
            parser.error(f"Файл не найден или недоступен: {file_path}")

    return args


def read_logs(file_paths, date_filter=None):
    logs = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    log_entry = json.loads(line.strip())
                    if date_filter:
                        log_date = datetime.fromisoformat(log_entry['@timestamp']).date()
                        if log_date != date_filter:
                            continue
                    logs.append(log_entry)
                except (json.JSONDecodeError, KeyError):
                    continue
    return logs


def generate_average_report(logs):
    endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})

    for log in logs:
        url = log.get('url', '')
        response_time = log.get('response_time', 0.0)
        endpoint_stats[url]['count'] += 1
        endpoint_stats[url]['total_time'] += response_time

    report = []
    for url, stats in endpoint_stats.items():
        average_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0.0
        report.append({
            'endpoint': url,
            'request_count': stats['count'],
            'average_response_time': round(average_time, 3)
        })

    return sorted(report, key=lambda x: -x['request_count'])


def generate_user_agents_report(logs):
    ua_stats = defaultdict(int)

    for log in logs:
        ua = log.get('http_user_agent', 'Unknown')
        ua_stats[ua] += 1

    return [{'user_agent': k, 'count': v} for k, v in sorted(ua_stats.items(), key=lambda x: -x[1])]


def print_report(report_data, report_type):
    if not report_data:
        print("Нет данных для отображения")
        return

    try:
        if report_type == 'average':
            headers = ['№', 'endpoint', 'request_count', 'avg_time']
            table_data = [
                [i + 1, item.get('endpoint', 'N/A'),
                 item.get('request_count', 0),
                 item.get('average_response_time', 0)]
                for i, item in enumerate(report_data)
            ]
        else:
            headers = ['№', 'user_agent', 'count']
            table_data = [
                [i + 1, item.get('user_agent', 'Unknown'),
                 item.get('count', 0)]
                for i, item in enumerate(report_data)
            ]

        print(tabulate(table_data, headers=headers))
    except Exception as e:
        print(f"Ошибка при выводе отчета: {str(e)}")


def main():
    args = parse_args()

    date_filter = None
    if args.date:
        try:
            date_filter = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Неправильный формат даты. Ожидается: YYYY-MM-DD")
            return

    logs = read_logs(args.file, date_filter)

    if args.report == 'average':
        report = generate_average_report(logs)
        print_report(report, args.report)
    elif args.report == 'user_agents':
        report = generate_user_agents_report(logs)
        print_report(report, args.report)


if __name__ == '__main__':
    main()