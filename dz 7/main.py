# Комментарий для преподавателя:
#для удобства работы с аннотациями типов использую __future__
#не знаю нужно ли добавлять csv в репозиторий(вроде как бд, а бд нельзя комитить), но я его добавил на всякий случай
# Для запуска: python main.py -i "web_clients_correct-старое.csv" -o "descriptions.txt"



from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

@dataclass(frozen=True)
class Customer:
    name: str
    device_type: str
    browser: str
    sex: str
    age: int
    bill: int
    region: str


def read_csv_rows(path: str, encoding: str = "utf-8") -> List[Dict[str, str]]:
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV не содержит заголовков.")
        rows: List[Dict[str, str]] = []
        for row in reader:
            # DictReader может вернуть None для отсутствующих полей — нормализуем в строки
            rows.append({k: (v if v is not None else "") for k, v in row.items()})
        return rows


def detect_format(fieldnames: Sequence[str]) -> str:
    normalized = {normalize_key(x) for x in fieldnames}
    required = {"name", "device_type", "browser", "sex", "age", "bill", "region"}
    if required.issubset(normalized):
        return "columns"
    return "structured_text"


def normalize_key(key: str) -> str:
    """Нормализует имя колонки: lower + замена пробелов на '_'."""
    return re.sub(r"\s+", "_", key.strip().lower())


def parse_int(value: str, field: str) -> int:
    """Преобразует строку в int, вытаскивая цифры. Бросает ValueError при невозможности."""
    digits = re.findall(r"-?\d+", value.strip())
    if not digits:
        raise ValueError(f"Поле '{field}' не содержит числа: {value!r}")
    return int(digits[0])


def row_to_customer_from_columns(row: Dict[str, str], fieldnames: Sequence[str]) -> Customer:
    """Парсит строку CSV с отдельными колонками."""
    # Маппинг: normalized_header -> original_header
    header_map = {normalize_key(h): h for h in fieldnames}

    def get(norm_key: str) -> str:
        orig = header_map.get(norm_key)
        return row.get(orig, "").strip() if orig else ""

    return Customer(
        name=get("name"),
        device_type=get("device_type"),
        browser=get("browser"),
        sex=get("sex"),
        age=parse_int(get("age"), "age"),
        bill=parse_int(get("bill"), "bill"),
        region=get("region"),
    )


def parse_structured_text_blob(blob: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    lines = [ln.strip() for ln in blob.splitlines() if ln.strip()]
    for line in lines:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip()
    return result


def row_to_customer_from_structured_text(row: Dict[str, str]) -> Customer:
    blob = "\n".join(v for v in row.values() if v is not None)
    data = parse_structured_text_blob(blob)

    name = data.get("ФИО", "").strip()
    sex = data.get("Пол", "").strip()
    age = parse_int(data.get("Возраст", ""), "Возраст")
    device = data.get("Устройство, с которого выполнялась покупка", "").strip()
    browser = data.get("Браузер", "").strip()
    bill = parse_int(data.get("Сумма чека", ""), "Сумма чека")
    region = data.get("Регион покупки", "").strip()

    return Customer(
        name=name,
        device_type=device,
        browser=browser,
        sex=sex,
        age=age,
        bill=bill,
        region=region,
    )


def parse_customers(rows: List[Dict[str, str]], fieldnames: Sequence[str]) -> List[Customer]:
    fmt = detect_format(fieldnames)
    customers: List[Customer] = []

    for row in rows:
        if fmt == "columns":
            customers.append(row_to_customer_from_columns(row, fieldnames))
        else:
            customers.append(row_to_customer_from_structured_text(row))

    return customers


def russian_year_word(age: int) -> str:
    n = abs(age)
    last_two = n % 100
    last = n % 10
    if 11 <= last_two <= 14:
        return "лет"
    if last == 1:
        return "год"
    if 2 <= last <= 4:
        return "года"
    return "лет"


def sex_phrase_ru(sex: str) -> Tuple[str, str]:
    s = sex.strip().lower()
    if s in {"female", "ж", "жен", "женский", "женщина"}:
        return "женского пола", "совершила"
    if s in {"male", "м", "муж", "мужской", "мужчина"}:
        return "мужского пола", "совершил"
    return "не указанного пола", "совершил(а)"


def device_phrase_ru(device_type: str) -> str:
    d = device_type.strip().lower()

    mapping = {
        "mobile": "мобильного устройства",
        "phone": "мобильного телефона",
        "smartphone": "смартфона",
        "tablet": "планшета",
        "laptop": "ноутбука",
        "notebook": "ноутбука",
        "desktop": "компьютера",
        "pc": "компьютера",
    }

    return mapping.get(d, device_type.strip() or "устройства")


def build_description(customer: Customer) -> str:
    sex_text, verb = sex_phrase_ru(customer.sex)
    years_word = russian_year_word(customer.age)
    device_text = device_phrase_ru(customer.device_type)

    return (
        f"Пользователь {customer.name} {sex_text}, {customer.age} {years_word} {verb} покупку на "
        f"{customer.bill} у.е. с {device_text} в браузере {customer.browser}. "
        f"Регион, из которого совершалась покупка: {customer.region}."
    )


def build_descriptions(customers: Iterable[Customer]) -> List[str]:
    return [build_description(c) for c in customers]


def write_txt(path: str, lines: Sequence[str], encoding: str = "utf-8") -> None:
    with open(path, "w", encoding=encoding, newline="\n") as f:
        for i, line in enumerate(lines):
            f.write(line.rstrip() + "\n")
            if i != len(lines) - 1:
                f.write("\n")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генератор текстовых описаний покупателей из CSV."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Путь к входному CSV файлу.",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Путь к выходному TXT файлу.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Кодировка входного и выходного файлов (по умолчанию utf-8).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    rows = read_csv_rows(args.input, encoding=args.encoding)
    
    with open(args.input, "r", encoding=args.encoding, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        
    customers = parse_customers(rows, fieldnames)
    descriptions = build_descriptions(customers)
    write_txt(args.output, descriptions, encoding=args.encoding)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
