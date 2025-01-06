import asyncio
import logging
from datetime import timedelta, datetime

import requests
from aiogram import Bot, Dispatcher,  types
from aiogram.filters import Command

# Конфигурация
WB_API_KEY = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQxMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1MTY4NTY1MywiaWQiOiIwMTk0MmNjMS00ZWQ3LTcwOTgtYTU0Yy05NGExNjc1Y2UwZTAiLCJpaWQiOjEzNjg0NzEzNSwib2lkIjozOTcwMDI1LCJzIjoxMDczNzQ5NzU4LCJzaWQiOiJhYTRjNGEyZS0zYzRmLTQ3YzUtYTE2Yy0xNWVjZGUyMWI5MDMiLCJ0IjpmYWxzZSwidWlkIjoxMzY4NDcxMzV9.Glp7c55seZsPeFIs25MESK9bCEOStKgq7yTfYiOhW8zgfO2kP4vK-9k5b_xea6_RL6aI_zC-QAjmXH9fZ6fCkw"
TELEGRAM_BOT_TOKEN = "7485901146:AAG9xnPvf1WxxqpH1HJQ_0dI2yj0dGxyRhA"
TELEGRAM_CHAT_ID = "7065054223"
WB_ORDERS_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
WB_SALES_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"
WB_STOCK_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"


# Инициализация бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Получение данных с API Wildberries
def fetch_data(api_url, date_from):
    headers = {
        "Authorization": WB_API_KEY
    }
    params = {"dateFrom": date_from, "flag": 0}
    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
        return []


# Форматирование уведомлений
def format_notification(data, data_type="orders"):
    messages = []
    for item in data:
        if item.get("isCancel", False):
            status = "🚫 Отмена"
        elif item.get("isSupply", False):
            status = "✅ Выкуп"
        else:
            status = "🛒 Заказ"

        message = f"{status} "

        if data_type == "orders":
            message += f"[№{item.get('gNumber', 'Нет данных')}]: {item.get('finishedPrice', 0)}₽\n"
            message += f"📈 Сегодня: {item.get('priceWithDisc', 0)}₽\n"
            message += f"🕒 Дата и время: {item.get('date')}\n"
            message += f"🆔 Арт: {item.get('nmId', 'Нет данных')} (https://www.wildberries.ru/catalog/{item.get('nmId', 'нет_данных')}/detail.aspx)\n"
            message += f"📁 Категория: {item.get('category', 'Нет данных')} / {item.get('subject', 'Нет данных')}\n"
            message += f"🏷 {item.get('brand', 'Нет данных')} (https://www.wildberries.ru/catalog/{item.get('nmId', 'нет_данных')}/detail.aspx)\n"
            message += f"🛍 WB скидка: {item.get('spp', 0)}₽ ({item.get('discountPercent', 0)}%)\n"
            message += f"🔢 Баркод: {item.get('barcode', 'Нет данных')}\n"
            message += f"⭐️ Рейтинг: {item.get('rating', 'Нет данных')}\n"
            message += f"💬 Отзывы: {item.get('reviews', 0)}\n"
            message += f"💼 Комиссия: {item.get('commission', 'Нет данных')}%\n"
            message += f"🌐 Склад: {item.get('warehouseName', 'Нет данных')} → {item.get('regionName', 'Нет данных')}: {item.get('Price', 'Нет данных')}\n"
            message += f"🚛 В пути к клиенту: {item.get('inWayToClient', 'Нет данных')} шт.\n"
            message += f"🚚 В пути возвраты: {item.get('returnedToSupplier', 'Нет данных')} шт.\n"
            message += f"📦 Остатки: {item.get('quantityFull', 'Нет данных')} шт.\n"

        elif data_type == "sales":
            message += f"Продажа на сумму: {item.get('forPay', 0)}₽\n"
            message += f"Дата продажи: {item.get('date', 'Нет данных')}\n"
            message += f"Количество: {item.get('quantity', 0)}\n"

        elif data_type == "stocks":
            message += f"Склад: {item.get('warehouseName', 'Нет данных')} ({item.get('quantityFull', 0)} шт.)\n"
            message += f"Артикул: {item.get('nmId', 'Нет данных')}\n"
            message += f"Баркод: {item.get('barcode', 'Нет данных')}\n"
            message += f"🌐 Склад: {item.get('warehouseName', 'Нет данных')} → {item.get('regionName', 'Нет данных')}: {item.get('Price', 'Нет данных')}\n"
            message += f"🚛 В пути к клиенту: {item.get('inWayToClient', 'Нет данных')} шт.\n"
            message += f"🚚 В пути возвраты: {item.get('returnedToSupplier', 'Нет данных')} шт.\n"

        messages.append(message)
    return messages


async def send_telegram_message(messages):
    for message in messages:
        try:
            await bot.send_message(TELEGRAM_CHAT_ID, message)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")


# Команда для тестирования
@dp.message(Command("notify"))
async def notify_handler(message: types.Message):
    logger.info(f"Получена команда /notify от пользователя {message.from_user.id}")
    await message.reply("Получаем данные...")

    try:
        date_from = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        orders = fetch_data(WB_ORDERS_URL, date_from)
        sales = fetch_data(WB_SALES_URL, date_from)
        stocks = fetch_data(WB_STOCK_URL, date_from)

        order_messages = format_notification(orders, data_type="orders")
        sale_messages = format_notification(sales, data_type="sales")
        stock_messages = format_notification(stocks, data_type="stocks")

        all_messages = order_messages + sale_messages + stock_messages
        if all_messages:
            await send_telegram_message(all_messages)
        else:
            await message.reply("Нет данных за указанный период.")

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await message.reply(f"Произошла ошибка: {e}")


# Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())




"""
{
        "realizationreport_id": 285599980,
        "date_from": "2024-11-04",
        "date_to": "2024-11-10",
        "create_dt": "2024-11-11",
        "currency_name": "KGS",
        "suppliercontract_code": null,
        "rrd_id": 2793040446336,
        "gi_id": 0,
        "dlv_prc": 0,
        "fix_tariff_date_from": "",
        "fix_tariff_date_to": "",
        "subject_name": "",
        "nm_id": 0,
        "brand_name": "",
        "sa_name": "",
        "ts_name": "",
        "barcode": "",
        "doc_type_name": "",
        "quantity": 2,
        "retail_price": 0,
        "retail_amount": 0,
        "sale_percent": 0,
        "commission_percent": 0,
        "office_name": "",
        "supplier_oper_name": "Возмещение издержек по перевозке/по складским операциям с товаром",
        "order_dt": "2024-11-05T00:00:00Z",
        "sale_dt": "2024-11-05T00:00:00Z",
        "rr_dt": "2024-11-05",
        "shk_id": 10471309102,
        "retail_price_withdisc_rub": 0,
        "delivery_amount": 0,
        "return_amount": 0,
        "delivery_rub": 0,
        "gi_box_type_name": "",
        "product_discount_for_report": 0,
        "supplier_promo": 0,
        "rid": 0,
        "ppvz_spp_prc": 0,
        "ppvz_kvw_prc_base": 0,
        "ppvz_kvw_prc": 0,
        "sup_rating_prc_up": 0,
        "is_kgvp_v2": 0,
        "ppvz_sales_commission": 0,
        "ppvz_for_pay": 0,
        "ppvz_reward": 0,
        "acquiring_fee": 0,
        "acquiring_percent": 0,
        "payment_processing": "",
        "acquiring_bank": "",
        "ppvz_vw": -1.25,
        "ppvz_vw_nds": -0.15,
        "ppvz_office_name": "",
        "ppvz_office_id": 0,
        "ppvz_supplier_id": 0,
        "ppvz_supplier_name": "",
        "ppvz_inn": "",
        "declaration_number": "",
        "sticker_id": "0",
        "site_country": "",
        "srv_dbs": false,
        "penalty": 0,
        "additional_payment": 0,
        "rebill_logistic_cost": 1.4,
        "storage_fee": 0,
        "deduction": 0,
        "acceptance": 0,
        "assembly_id": 0,
        "srid": "b27fa7cc5f8f472a8e014380259268a4",
        "report_type": 1,
        "is_legal_entity": false,
        "trbx_id": ""
    },
"""