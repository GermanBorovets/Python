year = int(input("Введите год (четырехзначное число): "))

if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
    print("Високосный год")
else:
    print("Обычный год")