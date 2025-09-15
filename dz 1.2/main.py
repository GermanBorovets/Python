number = int(input("Введите шестизначный номер билета: "))

digits = str(number)
first_sum = int(digits[0]) + int(digits[1]) + int(digits[2])
last_sum = int(digits[3]) + int(digits[4]) + int(digits[5])
    
if first_sum == last_sum:
    print("Счастливый билет")
else:
    print("Несчастливый билет")