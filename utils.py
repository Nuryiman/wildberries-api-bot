import json
from datetime import datetime

import requests


WB_ORDERS_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
WB_SALES_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"
WB_STOCK_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
WB_REPORT_URL = "https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod"
WB_PING_URL = "https://common-api.wildberries.ru/ping"



def check_api_token(api_token):
    try:
        headers = {
            'Authorization': api_token
        }
        response = requests.get(WB_PING_URL, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False


def check_shop_api(data: dict) -> bool:
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    except json.JSONDecodeError:
        return True

    for user in json_data:
        if user['telegram_id'] == data['telegram_id']:
            for item in user['shops']:
                if item['api_token'] == data['api_token']:
                    return False
    return True


def add_shop(data: dict) -> bool:
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    except json.JSONDecodeError:
        json_data = []

    for user in json_data:
        if user['telegram_id'] == data['telegram_id']:
            for item in user['shops']:
                if item['api_token'] == data['api_token'] or item['shop_name'] == data['shop_name']:
                    return False
            user['shops'].append({
                'api_token': data['api_token'],
                'shop_name': data['shop_name']
            })
            with open('config.json', 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)

            return True

    json_data.append({
        'telegram_id': data['telegram_id'],
        'shops': [
            {
                'api_token': data['api_token'],
                'shop_name': data['shop_name']
            }
        ]
    })
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

    return True


def get_all_user_shops(user_id: int) -> list:

    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            
    except json.JSONDecodeError:
        return []

    for user in json_data:
        if user['telegram_id'] == user_id:
            return [item['shop_name'] for item in user['shops']]


def get_shop_api_token(user_id, shop_name):
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        for user in json_data:
            if user['telegram_id'] == user_id:
                for item in user['shops']:
                    if item['shop_name'] == shop_name:
                        return item['api_token']
    except json.JSONDecodeError:
        return False


def delete_shop(user_id: int, shop_name: str):
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    except json.JSONDecodeError:
        return False

    for user in json_data:
        if user['telegram_id'] == user_id:
            for item in user['shops']:
                if item['shop_name'] == shop_name:
                    user['shops'].remove(item)
                    with open('config.json', 'w', encoding='utf-8') as file:
                        json.dump(json_data, file, indent=4, ensure_ascii=False)
                    return True
    return False


# Получение данных с API Wildberries
def fetch_data(api_url, date_from, date_to, api_token):
    headers = {
        "Authorization": api_token
    }
    params = {"dateFrom": date_from, "dateTo": date_to, "flag": 0}
    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
        return []


def get_sales_report(user_id, shop_name, date_from, date_to):
    message = " "
    api_token = get_shop_api_token(user_id, shop_name)
    sales_data = fetch_data(WB_REPORT_URL, date_from, date_to, api_token)
    print(sales_data)
    count_sales = len(sales_data)

    messages = [f"📦Сумма всех продаж: {count_sales} шт.\n"]

    for item in sales_data:

        message = "✅ Продажа\n"
        message += f"🔖Цена: {item.get('retail_price', 0)}₽\n"
        message += f"⭐ Бренд: {item.get('brand_name', 'Нет данных')} / {item.get('subject_name', 'Нет данных')}\n"
        message += f"🛍 Количество: {item.get('quantity', 0)}шт.\n"
        message += f"💼 Комиссия: {item.get('commission_percent', 'Нет данных')}%\n"
        message += f"🛍 WB скидка: {item.get('spp', 0)}₽ ({item.get('sale_percent', 0)}%)\n"
        message += f"💳 Стоимость эквайринга: {item.get('acquiring_percent', 'Нет данных')}%\n"
        message += f"🚛 Стоимость логистики: {item.get('delivery_rub', 'Нет данных')}₽\n"
        message += f"🗄 Стоимость хранения: {item.get('storage_fee', 'Нет данных')}₽\n"
        messages.append(message)

    return messages


def is_valid_date(date_str: str) -> bool:
    try:
        # Проверяем формат даты: ГГГГ-ММ-ДД
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        # Если формат или дата некорректны
        return False