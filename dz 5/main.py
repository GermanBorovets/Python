from datetime import datetime


date_str = input("Введите дату в формате ГГГГ-ММ-ДД: ")

date_obj = datetime.strptime(date_str, "%Y-%m-%d")

moscow_times = date_obj.strftime("%A, %B %d, %Y")
guardian = date_obj.strftime("%A, %d.%m.%y")
daily_news = date_obj.strftime("%A, %d %B %Y")

print("The Moscow Times —", moscow_times)
print("The Guardian —", guardian)
print("Daily News —", daily_news)