import os
import re
import json
import requests
from datetime import datetime

# URL с данными
url = os.getenv("URL2", "https://giamping.com/repository/vpnrequestmobile.php?message=MBVRvEzBAVRWJST8NhVTRCAKbh2gO2ztsF5pwbdVfjd1UaqvsdTg9K122p1JxkuXgILF5npSo48jFf9ZAPnSe2rIRxq3QCGClEu21YSWLU6F3Nvf0XMJ2LU34sHuKa8go0DN0vHaf2OEFYNrhcXcGpozFezCj8OlN8cPzPrnIsLLMzBeTcglmF0jFS9gZZQipqU/3pbsftSRlUY1j5/BMpGPVPNhWMxE4m71qx7Ryfy5j967hXwjrP7dhrH63izHZyhbQIGPVPNXQXB1nf70ftqAgVEQNw==")

# Получение сегодняшней даты
today = datetime.now().strftime('%Y-%m-%d')

# Путь для сохранения файлов
data_dir = os.path.join(os.getcwd(), "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Путь для сохранения JSON файлов
today_json_file = os.path.join(data_dir, f"{today}.json")
db_file = os.path.join(data_dir, "db.json")
files_info_file = os.path.join(data_dir, "files.json")

# Регулярное выражение для парсинга строк
pattern = re.compile(
    r"(?P<session_id>\d+)•(?P<sessions>\d+) SESSIONS.*?USERS•(?P<location_info>.*?)•(?P<hostname>VPN[0-9]+\.OPENGW\.NET)(?::(?P<port>\d+))?•(?P<country_info>.*?)★VPNGATE★•(?P<ip>[0-9.]+)↓"
)

# Функция для парсинга строки
def parse_line(line):
    match = pattern.search(line)
    if match:
        data = match.groupdict()

        # Обработка данных
        ip = data.get("ip")
        # Если порт не указан, то использовать 443
        port = int(data.get("port")) if data.get("port") else 443
        hostname = data.get("hostname")
        sessions = data.get("sessions")

        # Парсинг информации о стране
        country_info = data.get("country_info")
        location_split = country_info.split("-")
        
        # Извлечение полного названия страны и кода
        if len(location_split) > 1:
            short_country = location_split[0].strip()  # Код страны (например, "JP")
            country_full = location_split[1].strip().split("~")[0].strip()  # Полное название страны, удаляя всё после "~"
        else:
            short_country = ""
            country_full = country_info.strip()

        return {
            "hostname": hostname,
            "ip": ip,
            "port": port,  # Теперь всегда есть порт
            "info": sessions,
            "info2": data.get("location_info"),
            "location": {
                "country": country_full,  # Полное название страны
                "short": short_country      # Код страны
            },
            "id": hostname.split("VPN")[-1],
            "key": f"{ip}:{port}"
        }
    else:
        print(f"Line did not match: {line}")
        return None

# Функция для получения данных
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        text_data = response.text
        print(f"Fetched data: {text_data[:500]}")  # Выводим часть данных для проверки
        return text_data.splitlines()
    else:
        print(f"Error fetching data. Status code: {response.status_code}")
        return []

# Функция для сохранения данных в JSON
def save_data_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Обновление файла db.json с уникальными IP:Port
def update_db(ip_port_list, db_file):
    existing_data = set()  # Используем множество для уникальности

    # Загружаем существующие IP:Port
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            existing_data = set(json.load(f))  # Загружаем в множество

    # Добавляем новые уникальные комбинации IP:Port
    for ip_port in ip_port_list:
        existing_data.add(ip_port)

    # Сохраняем обновлённый список в db.json
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(list(existing_data), f, ensure_ascii=False, indent=4)

# Обновление файла files.json с информацией о файлах
def update_files_info(data_dir, files_info_file):
    file_data = []
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".json") and file_name not in ["db.json", "files.json"]:
            file_path = os.path.join(data_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)

            # Подсчёт количества уникальных IP-адресов
            unique_ips = len(set([entry['key'] for entry in file_content]))
            # Размер файла в байтах
            byte_size = os.path.getsize(file_path)

            file_data.append({
                "name": file_name,
                "sstpCount": unique_ips,
                "byteSize": byte_size
            })

    # Сохраняем обновлённую информацию о файлах
    with open(files_info_file, 'w', encoding='utf-8') as f:
        json.dump(file_data, f, ensure_ascii=False, indent=4)

# Основная логика
if __name__ == "__main__":
    lines = fetch_data(url)
    parsed_data = [parse_line(line) for line in lines if "SESSIONS" in line]

    # Удаляем None из данных
    parsed_data = [data for data in parsed_data if data is not None]

    # Сохраняем данные в файл за сегодня
    save_data_to_json(parsed_data, today_json_file)

    # Обновляем db.json с новыми уникальными IP:Port
    ip_port_list = [entry['key'] for entry in parsed_data]
    update_db(ip_port_list, db_file)

    # Обновляем информацию о файлах в files.json
    update_files_info(data_dir, files_info_file)

    print(f"Данные успешно сохранены в файл {today_json_file}")
    print(f"db.json и files.json обновлены.")
