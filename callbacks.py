import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from states import CustomPeriodState, AddShopState
from keyboards import confirm_delete_shop_kb, get_shop_list_for_delete_kb, periods_kb, get_shop_list_for_report_kb
from utils import delete_shop, get_all_user_shops, get_sales_report


router = Router()


@router.callback_query(F.data.startswith("shop_del"))
async def handle_shop_callback(callback_query: CallbackQuery):
    _, shop_name = callback_query.data.split(" ", 1)
    await callback_query.message.edit_text(f"Подтвердите удаление магазина: {shop_name}", reply_markup=confirm_delete_shop_kb(shop_name))


@router.callback_query(F.data.startswith("cancel"))
async def cancel_callback(callback_query: CallbackQuery):
    await callback_query.message.delete()


@router.callback_query(F.data.startswith("confirm_delete"))
async def handle_shop_callback(callback_query: CallbackQuery):
    _, shop_name = callback_query.data.split(" ", 1)
    user_id = callback_query.from_user.id
    result = delete_shop(user_id, shop_name)
    if not result:
        await callback_query.message.edit_text("Не удалось найти магазин")
        return
    await callback_query.message.edit_text("Магазин успешно удален")


@router.callback_query(F.data.startswith("cancel_delete"))
async def cancel_delete_shop_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    shop_list = get_all_user_shops(user_id)
    await callback_query.message.edit_text(f"Выберите магазин, которого хотите удалить:",
                                           reply_markup=get_shop_list_for_delete_kb(shop_list))


@router.callback_query(F.data.startswith('shop_report'))
async def choice_shop_for_report_callback(callback_query: CallbackQuery):
    _, shop_name = callback_query.data.split(" ", 1)
    user_id = callback_query.from_user.id
    await callback_query.message.edit_text("Выберите период: ", reply_markup=periods_kb(shop_name))


@router.callback_query(F.data.startswith("Period"))
async def report_output(callback_query: CallbackQuery, state: FSMContext):
    _, period, shop_name = callback_query.data.split(" ", 2)

    user_id = callback_query.from_user.id

    if period == "last_seven_days":
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(days=7)
        print(date_from)

    elif period == "today":
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(days=1)

    elif period == "yesterday":
        date_to = datetime.datetime.now() - datetime.timedelta(days=1)
        date_from = date_to - datetime.timedelta(days=1)

    elif period == "custom_period":
        await callback_query.message.answer("Введите даты в формате YYYY-MM-DD YYYY-MM-DD\n"
                                               "Пример: <b>2024-06-06 2024-07-06</b>")
        await state.set_data({"shop_name": shop_name})
        await state.set_state(CustomPeriodState.custom_period)
        return

    else:
        await callback_query.message.answer("Ошибка при получении отчета")
        return

    msg = await callback_query.message.answer("Высчитываем отчет...")
    date_from = date_from.strftime("%Y-%m-%dT%H:%M:%S")
    date_to = date_to.strftime("%Y-%m-%dT%H:%M:%S")
    print(date_from, date_to)
    result = get_sales_report(user_id, shop_name, date_from, date_to)
    await msg.delete()
    print(result)
    if not result:
        await callback_query.message.answer("Произошла ошибка при получении отчета")
        return
    for item in result:
        try:
            await callback_query.message.answer(item)
        except Exception as e:
            await callback_query.message.answer(f"Произошла ошибка при отправки сообщения: {e}")


@router.callback_query(F.data == "addshop_call")
async def add_shop_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите API-токен:")
    await state.set_state(AddShopState.add_shop_api)


@router.callback_query(F.data == "delshop_call")
async def add_shop_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    print(user_id)
    shop_list = get_all_user_shops(user_id)
    if not shop_list:
        await callback_query.message.answer("У вас нет добавленных магазинов")
        return
    await callback_query.message.answer(f"Выберите магазин, которого хотите удалить:", reply_markup=get_shop_list_for_delete_kb(shop_list))


@router.callback_query(F.data == "shops_call")
async def shops_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    shop_list = get_all_user_shops(user_id)

    if not shop_list:
        await callback_query.message.answer("У вас нет добавленных магазинов.")
        return

    shop_list_text = "\n".join([f"{i + 1}. <b>{item}</b>" for i, item in enumerate(shop_list)])

    await callback_query.message.answer(f"Ваши магазины:\n{shop_list_text}", parse_mode="HTML")


@router.callback_query(F.data == "report_call")
async def report_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    shop_list = get_all_user_shops(user_id)
    if not shop_list:
        await callback_query.message.answer("У вас нет добавленных магазинов.")
        return

    await callback_query.message.answer("Выберите магазин: ", reply_markup=get_shop_list_for_report_kb(shop_list))

