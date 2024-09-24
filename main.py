import re
import json
import os
import sys
from loguru import logger

# Настройка Loguru без логирования в файл
logger.remove()  # Удаляем все предыдущие конфигурации логгирования
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

pattern = re.compile(
    r"(?P<session_id>\d+)•(?P<sessions>\d+) SESSIONS.*?USERS•(?P<location_info>.*?)•(?P<hostname>VPN[0-9A-Z]+\.OPENGW\.NET|[A-Z]+\.OPENGW\.NET)(?::(?P<port>[0-9]+))?•(?P<country_info>[^★]+)★VPNGATE★•(?P<ip>[0-9.]+)↓"
)

# Загружаем данные из db.json
def load_db(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохраняем JSON без отступов
def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))  # без отступов

# Парсинг строки
def parse_line(line):
    match = pattern.match(line)
    if not match:
        logger.warning(f"Line did not match: {line}")
        return None

    result = match.groupdict()
    
    # Парсим данные
    ip = result['ip']
    port = result['port'] if result['port'] else '443'  # Если порта нет, назначаем 443
    country_info = result['country_info'].split('~')[0].strip()  # Убираем информацию о компании
    
    # Код страны
    short = country_info.split(' ')[0]
    country = country_info.split(' ')[-1]
    
    logger.info(f"Parsed: {ip}:{port} - Country: {country} - Short: {short}")
    
    return {
        'ip': ip,
        'port': port,
        'country': country,
        'short': short
    }

# Обновляем db.json и files.json
def update_data():
    db_filepath = 'data/db.json'
    files_filepath = 'data/files.json'
    
    # Загружаем текущие IP из базы
    ip_list = load_db(db_filepath)
    
    # Пример строки для теста
    lines = [
        "0390943•54 SESSIONS 26 DAYS TOTAL 654,737 USERS•SOUTH AMERICA 43.09•SPIGBRAZIL.OPENGW.NET:1194•BR - BRAZIL ~ NET TURBO TELECOM ★VPNGATE★•186.209.48.54↓",
        "0375424•51 SESSIONS 89 DAYS TOTAL 460,483 USERS•ASIA 30.68•VPN157756716.OPENGW.NET•ID - INDONESIA•103.151.141.69↓"
    ]
    
    new_ips = []
    for line in lines:
        parsed = parse_line(line)
        if parsed:
            ip_port = f"{parsed['ip']}:{parsed['port']}"
            if ip_port not in ip_list:
                ip_list.append(ip_port)  # Добавляем новый IP
                new_ips.append(ip_port)
    
    # Сохраняем обновленную базу IP
    save_json(db_filepath, ip_list)
    
    # Обновляем files.json
    if not os.path.exists('data'):
        os.makedirs('data')
    
    file_list = []
    for file in os.listdir('data'):
        if file not in ['db.json', 'files.json']:
            filepath = os.path.join('data', file)
            size = os.path.getsize(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                sstp_count = len(content)
            
            file_list.append({
                'name': file,
                'sstpCount': sstp_count,
                'byteSize': size
            })
    
    save_json(files_filepath, file_list)
    
    logger.info(f"Added {len(new_ips)} new IP addresses.")

if __name__ == "__main__":
    update_data()
