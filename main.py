import os
import re
import json
import requests
from datetime import datetime
from loguru import logger

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

# Обновлённое регулярное выражение для парсинга строк
pattern = re.compile(
    r"(?:↑)?(?P<session_id>\d+)•(?P<sessions>\d+) SESSIONS.*?USERS•(?P<location_info>.*?)•(?P<hostname>[A-Z0-9-]+\.OPENGW\.NET)(?::(?P<port>[0-9]+))?•(?P<country_info>.+?)•(?P<ip>[0-9.]+)(?:↓)?"
)

# Логи с настройками
logger.remove()  # Убираем стандартный вывод
logger.add(lambda msg: print(msg, end=""), format="{time} | {level} | {message}", level="DEBUG")

# Функция для парсинга строки
def parse_line(line):
    match = pattern.search(line)
    if match:
        data = match.groupdict()

        # Обработка данных
        ip = data.get("ip")
        port = int(data.get("port")) if data.get("port") else 443
        hostname = data.get("hostname")
        location_info = data.get("location_info").split(" ")
        sessions = data.get("sessions")
        country_info = data.get("country_info")

        location_split = country_info.split("~")
        country_full = location_split[0].strip()
        location_name = location_split[1].strip() if len(location_split) > 1 else ""

        country_split = country_full.split("-")
        short_country = country_split[1].strip() if len(country_split) > 1 else ""

        return {
            "hostname": hostname,
            "ip": ip,
            "port": port,
            "info": sessions,
            "info2": " ".join(location_info),
            "location": {
                "country": country_full,
                "short": short_country,
                "name": location_name
            },
            "id": hostname.split("VPN")[-1] if 'VPN' in hostname else hostname,
            "key": f"{ip}:{port}"
        }
    else:
        logger.debug(f"Line did not match: {line}")
        return None

# Функция для получения данных
def fetch_data(url):
    logger.info(f"Fetching data from URL: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        text_data = response.text
        logger.debug(f"Fetched data: {text_data[:500]}...")  # Выводим часть данных для проверки
        return text_data.splitlines()
    else:
        logger.error(f"Error fetching data. Status code: {response.status_code}")
        return []

# Функция для сохранения данных в JSON
def save_data_to_json(data, file_path):
    logger.info(f"Saving data to file: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Обновление файла db.json с уникальными IP:Port
def update_db(ip_port_list, db_file):
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Добавляем только новые комбинации IP:Port
    updated_data = list(set(existing_data + ip_port_list))

    logger.info(f"Updated db.json with {len(updated_data)} unique entries (removed duplicates).")
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)

# Обновление файла files.json с информацией о файлах
def update_files_info(data_dir, files_info_file):
    logger.info(f"Updating files info in {files_info_file}")
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

    logger.info(f"files.json updated with {len(file_data)} entries.")

# Основная логика
if __name__ == "__main__":
    lines = fetch_data(url)
    parsed_data = [parse_line(line) for line in lines if "SESSIONS" in line]

    # Удаляем None из данных
    parsed_data = [data for data in parsed_data if data is not None]

    # Сохраняем данные в файл за сегодня
    save_data_to_json(parsed_data, today_json_file)

    # Обновляем db.json с новыми IP:Port
    ip_port_list = [entry['key'] for entry in parsed_data]
    update_db(ip_port_list, db_file)

    # Обновляем информацию о файлах в files.json
    update_files_info(data_dir, files_info_file)

    logger.success(f"Данные успешно сохранены в файл {today_json_file}")
    logger.success(f"db.json и files.json обновлены.")
