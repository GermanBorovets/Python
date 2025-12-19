import csv


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sex_to_ru(sex):
    if sex.strip().lower() == "female":
        return "женского пола", "совершила"
    return "мужского пола", "совершил"


def device_to_ru(device_type):
    d = device_type.strip().lower()
    if d == "mobile":
        return "мобильного устройства"
    if d == "tablet":
        return "планшета"
    if d == "desktop":
        return "компьютера"
    return device_type


def build_description(row):
    sex_text, verb = sex_to_ru(row["sex"])
    device_text = device_to_ru(row["device_type"])

    return (
        f"Пользователь {row['name']} {sex_text}, {row['age']} лет {verb} покупку на "
        f"{row['bill']} у.е. с {device_text} в браузере {row['browser']}. "
        f"Регион, из которого совершалась покупка: {row['region']}."
    )


def write_txt(path, texts):
    with open(path, "w", encoding="utf-8") as f:
        for text in texts:
            f.write(text + "\n\n")


def main():
    input_file = "web_clients_correct-старое.csv"
    output_file = "clients.txt"

    rows = read_csv(input_file)
    descriptions = [build_description(row) for row in rows]
    write_txt(output_file, descriptions)


if __name__ == "__main__":
    main()
