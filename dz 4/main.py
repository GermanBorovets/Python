documents = [
    {'type': 'passport', 'number': '2207 876234', 'name': 'Василий Гупкин'},
    {'type': 'invoice', 'number': '11-2', 'name': 'Геннадий Покемонов'},
    {'type': 'insurance', 'number': '10006', 'name': 'Аристарх Павлов'}
]

directories = {
    '1': ['2207 876234', '11-2'],
    '2': ['10006'],
    '3': []
}

def get_p(doc_number):
    for doc in documents:
        if doc['number'] == doc_number:
            return doc['name']
    return None

def get_s(doc_number):
    for shelf, docs in directories.items():
        if doc_number in docs:
            return shelf
    return None


while True:
    command = input('Введите команду: ').strip().lower()
    if command == 'q':
        break
    elif command == 'p':
        doc_number = input('Введите номер документа: ').strip()
        p = get_p(doc_number)
        if p:
            print(f'Владелец документа: {p}')
        else:
            print('Документ не найден.')
    elif command == 's':
        doc_number = input('Введите номер документа: ').strip()
        s = get_s(doc_number)
        if s:
            print(f'Документ хранится на полке: {s}')
        else:
            print('Документ не найден.')
    else:
            print('Неизвестная команда. Попробуйте команды p, s или q')
