import argparse
import sys
import csv
import json
import os
import urllib.request
import urllib.error

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
        
        # Этап 2: Сбор данных
        self.dependencies = self.collect_dependencies()

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

    def collect_dependencies(self):
        """Этап 2: Сбор данных о зависимостях npm пакетов"""
        print(f"\nНачинаем сбор данных для пакета: {self.params['package_name']}")
        
        if self.params['test_mode']:
            return self.collect_dependencies_test()
        else:
            return self.collect_dependencies_npm()

    def collect_dependencies_npm(self):
        """Сбор зависимостей из npm репозитория"""
        package_name = self.params['package_name']
        repo_url = self.params['repo_url']
        
        try:
            # Формируем URL для npm registry API
            if 'registry.npmjs.org' in repo_url:
                npm_url = f"{repo_url}/{package_name}"
            else:
                npm_url = f"https://registry.npmjs.org/{package_name}"
            
            print(f"Запрос к: {npm_url}")
            
            # Запрашиваем информацию о пакете
            with urllib.request.urlopen(npm_url) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Получаем последнюю версию
            latest_version = data.get('dist-tags', {}).get('latest')
            if not latest_version:
                raise ValueError("Не удалось определить последнюю версию пакета")
            
            # Получаем зависимости для последней версии
            version_data = data.get('versions', {}).get(latest_version, {})
            dependencies = version_data.get('dependencies', {})
            
            # Выводим прямые зависимости (требование этапа)
            print(f"\nПрямые зависимости пакета '{package_name}' (версия {latest_version}):")
            print("=" * 50)
            
            if dependencies:
                for dep_name, dep_version in dependencies.items():
                    print(f"  • {dep_name}: {dep_version}")
            else:
                print("Пакет не имеет зависимостей!")
            
            print("=" * 50)
            
            return dependencies
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"Пакет '{package_name}' не найден в npm репозитории")
            else:
                raise ValueError(f"Ошибка при запросе к npm: {e}")
        except urllib.error.URLError as e:
            raise ValueError(f"Ошибка сети: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка при разборе JSON ответа: {e}")
        except Exception as e:
            raise ValueError(f"Неожиданная ошибка при сборе данных: {e}")

    def collect_dependencies_test(self):
        """Тестовый режим - используем заранее подготовленные данные"""
        print("Работаем в тестовом режиме")
        
        # Тестовые данные для популярных npm пакетов
        test_dependencies = {
            'react': {
                'loose-envify': '^1.1.0',
                'object-assign': '^4.1.1'
            },
            'express': {
                'accepts': '~1.3.8',
                'array-flatten': '1.1.1',
                'body-parser': '1.20.2',
                'content-disposition': '0.5.4',
                'cookie': '0.5.0',
                'cookie-signature': '1.0.6'
            },
            'lodash': {},  # lodash не имеет зависимостей
            'vue': {
                '@vue/compiler-sfc': '^3.3.0',
                '@vue/shared': '^3.3.0'
            }
        }
        
        package_name = self.params['package_name']
        
        if package_name in test_dependencies:
            dependencies = test_dependencies[package_name]
            
            print(f"\nПрямые зависимости пакета '{package_name}' (тестовый режим):")
            print("=" * 50)
            
            if dependencies:
                for dep_name, dep_version in dependencies.items():
                    print(f"  • {dep_name}: {dep_version}")
            else:
                print("Пакет не имеет зависимостей!")
            
            print("=" * 50)
            
            return dependencies
        else:
            # Если пакет не в тестовых данных, имитируем пустые зависимости
            print(f"\nПакет '{package_name}' не имеет зависимостей (тестовый режим)")
            return {}

def main():
    """Основная функция для запуска приложения"""
    try:
        # Создаем визуализатор (автоматически выполняет этап 1 и 2)
        visualizer = DependencyVisualizer(input_type='command_line')
        
        # Сообщение об успешном завершении этапов
        print("\nЭтап 1 выполнен успешно!")
        print("Этап 2 выполнен успешно! Данные о зависимостях собраны.")
        print("\nСтатистика:")
        print(f"   - Найдено зависимостей: {len(visualizer.dependencies)}")
        print(f"   - Пакет готов к анализу графа зависимостей")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

