import csv


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

