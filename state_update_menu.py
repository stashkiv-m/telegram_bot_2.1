import csv
import csv

# Глобальна змінна для зберігання станів меню
global_menu_stack = []


def update_menu_stack(file_path='menu_state.csv'):
    global global_menu_stack  # Використовуємо глобальну змінну

    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            # Читаємо перший рядок з файлу (очікуємо, що там всього один рядок)
            for row in reader:
                if row:
                    # Додаємо стан меню до глобального списку
                    global_menu_stack.append(row[0])  # Додаємо значення з першого стовпця
                    break  # Прериваємо цикл, оскільки очікується лише один рядок
    except FileNotFoundError:
        print(f"Файл {file_path} не знайдено. Переконайтеся, що файл існує.")

    return global_menu_stack


def menu_state():
    try:
        with open('menu_state.csv', 'r') as file:
            return file.read()
    except Exception as e:
        pass


def update_menu_state(state):
    with open('menu_state.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([state])



