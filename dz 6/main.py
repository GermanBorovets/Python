# Для преподавателя: это дз делал позже чем дз 7, поэтому все-же решил сразу прописать файлы в коде, чтобы не путаться с именами при проверке.


import csv
import json


def load_purchase_categories(path):
    purchases = {}

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            record = json.loads(line)
            user_id = record.get('user_id')
            category = record.get('category')
            purchases[user_id] = category

    return purchases


def process_visit_log(visit_path, purchases, output_path):
    with open(visit_path, 'r', encoding='utf-8') as visit_file, \
         open(output_path, 'w', encoding='utf-8', newline='') as output_file:

        reader = csv.DictReader(visit_file)
        writer = csv.writer(output_file)

        writer.writerow(['user_id', 'source', 'category'])

        for row in reader:
            user_id = row['user_id']

            if user_id in purchases:
                writer.writerow([
                    user_id,
                    row['source'],
                    purchases[user_id]
                ])


def main():
    purchase_log = 'purchase_log.txt'
    visit_log = 'visit_log__1_.csv'
    output_file = 'funnel.csv'

    purchases = load_purchase_categories(purchase_log)
    process_visit_log(visit_log, purchases, output_file)


if __name__ == '__main__':
    main()
