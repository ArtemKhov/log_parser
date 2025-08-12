import argparse
import json
from collections import defaultdict
from tabulate import tabulate


def parse_args():
    parser = argparse.ArgumentParser(description='Обработка лог-файлов и формирование отчетов')
    parser.add_argument('--file', nargs='+', required=True, help='Путь до лог-файла')
    parser.add_argument('--report', choices=['average'], required=True, help='Тип отчета')
    return parser.parse_args()


def read_logs(file_paths):
    logs = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
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


def print_report(report_data):
    headers = ['№', 'endpoint', 'request_count', 'average_response_time']
    table_data = [
        [i+1, item['endpoint'], item['request_count'], item['average_response_time']]
        for i, item in enumerate(report_data)
    ]
    print(tabulate(table_data, headers=headers))


def main():
    args = parse_args()

    logs = read_logs(args.file)

    if args.report == 'average':
        report = generate_average_report(logs)
        print_report(report)


if __name__ == '__main__':
    main()