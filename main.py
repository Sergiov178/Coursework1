import requests
import os
import json

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('YANDEX_DISK_TOKEN')

class YD:
    def __init__(self, token):
        self.headers = {'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        self.base_url = 'https://cloud-api.yandex.net'

    def create_folder(self, path):
        if not self.headers.get('Authorization') or self.headers['Authorization'] == 'OAuth None':
            print('Ошибка: токен Яндекс.Диска не найден')
            return False

        response = requests.put(
        f'{self.base_url}/v1/disk/resources',
            headers=self.headers,
            params={'path':path}
        )

        if response.status_code == 201:
            print(f'Папка "{path}" успешно создана')
            return True

        if response.status_code == 409:
            print(f'Папка "{path}" уже существует')
            return True

        print(f'Ошибка создания папки: {response.status_code}')
        print(response.text)
        return False

    def upload_file(self, path_file, path_yd):
        response = requests.get(
            f'{self.base_url}/v1/disk/resources/upload',
            headers=self.headers,
            params={
                'path': path_yd,
                'overwrite': 'true'
            }
        )

        if response.status_code != 200:
            print(f'Ошибка получения ссылки для загрузки: {response.status_code}')
            print(response.text)
            return False

        upload_url = response.json().get('href')

        with open(path_file, 'rb') as f:
            upload_response = requests.put(upload_url, files={'file': f})

        if upload_response.status_code in (201, 202):
            print(f'Файл {path_file} успешно загружен на Яндекс.Диск в {folder_name}')
            return True

        print(f'Ошибка загрузки файла: {upload_response.status_code}')
        print(upload_response.text)
        return False

def get_ip():
    url_ip = 'https://api.ipify.org/?format=json'
    response = requests.get(url_ip)

    if response.status_code == 200:
        ip = response.json()['ip']
        return ip

    print(f'Ошибка получения IP: {response.status_code}')
    return None

ip = get_ip()

def get_city_data(ip, file_name='city.json'):
    url_geo = f'https://ipinfo.io/{ip}/geo/format=json'
    response = requests.get(url_geo)

    if response.status_code == 200:
        data = response.json()

        city_data = {
            'ip': ip,
            'city': data.get('city')
        }

        print(f"Ваш IP-адрес: {ip}, Ваш город: {city_data['city']}")

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(city_data, f)

        print(f'Данные сохранены в файл {file_name}')

        return city_data

    print(f'Ошибка: {response.status_code}')
    return None
file_name = 'city.json'
get_city_data(ip, file_name)

yd = YD(TOKEN)

folder_name = 'AIE-4'
yd.create_folder(folder_name)

yd.upload_file(file_name, f'{folder_name}/{file_name}')

try:
    os.remove(file_name)
    print(f'Файл {file_name} успешно удалён')
except FileNotFoundError:
    print(f'Файл {file_name} не найден')
except PermissionError:
    print(f'У Вас прав на удаление файла {file_name}')
except Exception as e:
    print(f"Ошибка: {e}")

