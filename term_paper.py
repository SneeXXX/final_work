import requests
import json

group_name = "PY-126"
text_for_image = input("Введите текст для картинки: ")
yandex_token = input("Введите ваш токен Яндекс.Диска: ")

cat_api_url = f"https://cataas.com/cat/cute/says/{text_for_image}"

response = requests.get(cat_api_url)
if response.status_code != 200:
    print("Не удалось получить изображение с сайта cataas.com")
    exit()

headers = {
    "Authorization": f"OAuth {yandex_token}"
}
disk_path = f"/{group_name}"

create_folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
params = {"path": disk_path}
response_check = requests.get(create_folder_url, headers=headers, params=params)

if response_check.status_code == 404:
    create_response = requests.put(create_folder_url, headers=headers, params={"path": disk_path})
    if create_response.status_code not in [201, 202]:
        print("Не удалось создать папку на Яндекс.Диске")
        exit()

file_name = f"{text_for_image}.jpg"
file_path_on_disk = f"{disk_path}/{file_name}"

upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
params_upload = {
    "path": file_path_on_disk,
    "overwrite": "true"
}
response_upload = requests.get(upload_url, headers=headers, params=params_upload)
if response_upload.status_code != 200:
    print("Не удалось получить ссылку для загрузки файла")
    exit()

upload_href = response_upload.json().get("href")
if not upload_href:
    print("Нет ссылки для загрузки файла")
    exit()

upload_response = requests.put(upload_href, files={"file": response.content})
if upload_response.status_code not in [200, 201]:
    print("Не удалось загрузить файл на Яндекс.Диск")
    exit()

size_response = requests.get(
    "https://cloud-api.yandex.net/v1/disk/resources",
    headers=headers,
    params={"path": file_path_on_disk}
)

file_info = {}
if size_response.status_code == 200:
    size_bytes = size_response.json().get("size", 0)
    file_info[file_name] = size_bytes
else:
    print("Не удалось получить информацию о файле")

json_filename = "files_info.json"
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(file_info, json_file)

print(f"Файл {file_name} успешно загружен и информация сохранена в {json_filename}")
