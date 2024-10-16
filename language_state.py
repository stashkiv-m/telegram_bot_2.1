import csv


def language_state():
    try:
        with open('language_state.csv', 'r') as file:
            return file.read()
    except Exception as e:
        pass


def update_language_state(state):
    with open('language_state.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([state])