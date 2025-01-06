from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_shop_list_for_delete_kb(shops: list):
    builder = InlineKeyboardBuilder()
    for item in shops:
        builder.add(InlineKeyboardButton(text=item, callback_data=f"shop_del {item}"))
    builder.adjust(2)
    builder.button(text="Не удалять", callback_data="cancel")
    return builder.as_markup()


def get_shop_list_for_report_kb(shops: list):
    builder = InlineKeyboardBuilder()
    for item in shops:
        builder.add(InlineKeyboardButton(text=item, callback_data=f"shop_report {item}"))
    builder.adjust(2)
    return builder.as_markup()


def confirm_delete_shop_kb(shop_name: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_delete {shop_name}")
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data=f"cancel_delete")
            ]
        ]
    )


def periods_kb(shop_name):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сегодня", callback_data=f"Period today {shop_name}"),
                InlineKeyboardButton(text="Вчера", callback_data=f"Period yesterday {shop_name}"),
                InlineKeyboardButton(text="Последние 7 дней", callback_data=f"Period last_seven_days {shop_name}")
            ],
            [
                InlineKeyboardButton(text="Ввести произвольный период", callback_data=f"Period custom_period {shop_name}")
            ]
        ]
    )


action_list = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить магазин", callback_data="addshop_call"),
        ],
        [
            InlineKeyboardButton(text="Удалить магазин", callback_data="delshop_call")
        ],
        [
            InlineKeyboardButton(text="Список магазинов", callback_data="shops_call")
        ],
        [
            InlineKeyboardButton(text="Сформировать отчет", callback_data="report_call")
        ]
    ]
)