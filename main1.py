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
              params={'path': path}
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
              print(f'Файл {path_file} успешно загружен на Яндекс.Диск')
              return True

          print(f'Ошибка загрузки файла: {upload_response.status_code}')
          print(upload_response.text)
          return False

      def upload_json_data(self, data, path_yd):
          # ДОБАВЛЕНО: метод загружает JSON-данные напрямую на Яндекс.Диск без создания локального файла
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

          # ДОБАВЛЕНО: превращаем словарь Python в JSON-строку
          json_data = json.dumps(data, ensure_ascii=False, indent=4)

          # ДОБАВЛЕНО: кодируем строку в bytes, потому что requests.put отправляет тело файла
          upload_response = requests.put(
              upload_url,
              data=json_data.encode('utf-8')
          )

          if upload_response.status_code in (201, 202):
              print(f'Данные успешно загружены на Яндекс.Диск в {path_yd}')
              return True

          print(f'Ошибка загрузки данных: {upload_response.status_code}')
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


  def get_city_data(ip):
      # ИЗМЕНЕНО: file_name больше не нужен, потому что локальный файл не создается
      url_geo = f'https://ipinfo.io/{ip}/geo/format=json'
      response = requests.get(url_geo)

      if response.status_code == 200:
          data = response.json()

          city_data = {
              'ip': ip,
              'city': data.get('city')
          }

          print(f"Ваш IP-адрес: {ip}, Ваш город: {city_data['city']}")

          # УДАЛЕНО: запись в локальный файл city.json больше не нужна
          return city_data

      print(f'Ошибка: {response.status_code}')
      return None


  yd = YD(TOKEN)

  folder_name = 'AIE-4'
  yd.create_folder(folder_name)

  file_name = 'city.json'

  ip = get_ip()

  if ip:
      city_data = get_city_data(ip)

      if city_data:
          # ИЗМЕНЕНО: загружаем словарь city_data напрямую на Яндекс.Диск
          yd.upload_json_data(city_data, f'{folder_name}/{file_name}')

  Главная идея:

  city_data = get_city_data(ip)
  yd.upload_json_data(city_data, f'{folder_name}/city.json')

  Теперь city.json не создается на твоем компьютере. JSON формируется в памяти и сразу отправляется на
  Яндекс.Диск.
