items = {}

n = int(input("Введите количество товаров(для использования дефолтных данных, введите 0): "))

if n != 0:
    for i in range(n):
        key = input(f"\nВведите ключ товара #{i+1}: ")
        name = input("Введите название товара: ")
        count = int(input("Введите количество: "))
        price = float(input("Введите цену: "))

        items[key] = {'name': name, 'count': count, 'price': price}
else:
    items = {
        'milk15': {'name': 'молоко 1.5%', 'count': 34, 'price': 89.9},
        'cheese': {'name': 'сыр молочный 1 кг', 'count': 12, 'price': 990.9},
        'sausage': {'name': 'колбаса 1 кг', 'count': 122, 'price': 1990.9}
    }

price_less_20 = {key: (value['count'] < 20) for key, value in items.items()}

print("\nprice_less_20 = {")

for key, value in price_less_20.items():
    print(f" '{key}': {value}, ")
print('}')