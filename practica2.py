import argparse
import sys
import csv
import json
import os

class DependencyVisualizer:
    def __init__(self, input_type: str = 'command_line'):
        self.input_type = input_type
        self.params = {}
        
        if self.input_type == 'command_line':
            self.params = self.parse_command_line()
        elif self.input_type == 'csv_file':
            self.params = self.parse_csv_file()
        
        self.validate_params()
        self.print_params()

    def parse_command_line(self):
        """Парсинг аргументов командной строки для 19 варианта"""
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей пакетов (Вариант 19)',
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        # Обязательные параметры
        parser.add_argument(
            'package_name',
            type=str,
            help='Имя анализируемого пакета'
        )
        
        parser.add_argument(
            '--repo',
            '-r',
            type=str,
            required=True,
            help='URL-адрес репозитория или путь к файлу тестового репозитория'
        )
        
        # Опциональные параметры для 19 варианта
        parser.add_argument(
            '--test-mode',
            '-t',
            action='store_true',
            default=False,
            help='Режим работы с тестовым репозиторием'
        )
        
        parser.add_argument(
            '--output',
            '-o',
            type=str,
            default='dependency_graph',
            help='Имя сгенерированного файла с изображением графа'
        )
        
        parser.add_argument(
            '--ascii-tree',
            '-a',
            action='store_true',
            default=False,
            help='Режим вывода зависимостей в формате ASCII-дерева'
        )
        
        parser.add_argument(
            '--max-depth',
            '-d',
            type=int,
            default=10,
            help='Максимальная глубина анализа зависимостей'
        )
        
        args = parser.parse_args()
        
        return {
            'package_name': args.package_name,
            'repo_url': args.repo,
            'test_mode': args.test_mode,
            'output_file': args.output,
            'ascii_tree': args.ascii_tree,
            'max_depth': args.max_depth
        }

    def parse_csv_file(self):
        """Парсинг параметров из CSV файла"""
        params = {}
        
        try:
            with open('config_19.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parameter = row['parameter'].strip()
                    value = row['value'].strip()
                    
                    # Преобразование типов данных
                    if parameter in ['test_mode', 'ascii_tree']:
                        value = value.lower() in ['true', '1', 'yes', 'y']
                    elif parameter == 'max_depth':
                        value = int(value) if value else 10
                    else:
                        value = value
                    
                    params[parameter] = value
            
            # Проверка обязательных полей
            required_fields = ['package_name', 'repo_url']
            for field in required_fields:
                if field not in params or not params[field]:
                    raise ValueError(f"Обязательный параметр '{field}' отсутствует или пуст")
            
            # Установка значений по умолчанию для необязательных полей
            params.setdefault('test_mode', False)
            params.setdefault('output_file', 'dependency_graph')
            params.setdefault('ascii_tree', False)
            params.setdefault('max_depth', 10)
            
            return params
            
        except FileNotFoundError:
            raise FileNotFoundError("Файл config_19.csv не найден")
        except Exception as e:
            raise ValueError(f"Ошибка при чтении CSV файла: {e}")

    def validate_params(self):
        """Валидация параметров"""
        # Проверка обязательных полей
        if not self.params.get('package_name'):
            raise ValueError("Имя пакета не может быть пустым")
        
        if not self.params.get('repo_url'):
            raise ValueError("URL репозитория не может быть пустым")
        
        # Проверка максимальной глубины
        if self.params['max_depth'] <= 0:
            raise ValueError("Максимальная глубина должна быть положительным числом")
        
        # Проверка корректности имени выходного файла
        output_file = self.params['output_file']
        if not output_file or not isinstance(output_file, str):
            raise ValueError("Имя выходного файла должно быть непустой строкой")

    def print_params(self):
        """Вывод всех параметров в формате ключ-значение (требование этапа)"""
        print("=== Параметры конфигурации (Вариант 19) ===")
        print(f"Имя анализируемого пакета: {self.params['package_name']}")
        print(f"URL/путь к репозиторию: {self.params['repo_url']}")
        print(f"Режим тестирования: {'включен' if self.params['test_mode'] else 'выключен'}")
        print(f"Имя выходного файла: {self.params['output_file']}")
        print(f"Режим ASCII-дерева: {'включен' if self.params['ascii_tree'] else 'выключен'}")
        print(f"Максимальная глубина: {self.params['max_depth']}")
        print("============================================")

def main():
    """Основная функция для запуска приложения"""
    try:
        # Можно легко переключаться между command_line и csv_file
        visualizer = DependencyVisualizer(input_type='command_line')
        
        # Сообщение о готовности к следующим этапам
        print("\n✅ Этап 1 выполнен успешно!")
        print("Конфигурация загружена. Приложение готово к реализации этапа 2.")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()