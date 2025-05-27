import requests

url = "https://adv.ltcrm.ru/api/api-leads"
token = "2|UnAttmvig4wPGEcblZj6Zt9jNY1sOMccjW0kVmLd"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "name": "Тест",
    "phone": "Телефон",
    "message": "Текст",
    "city": "Регион",
    "source": "Источник"
}

response = requests.post(url, json=data, headers=headers, verify=False)  # verify=False отключает SSL-проверку (как в PHP)

print("Status code:", response.status_code)
print("Response body:", response.text)
