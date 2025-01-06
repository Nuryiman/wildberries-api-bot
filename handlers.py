from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from keyboards import get_shop_list_for_delete_kb, get_shop_list_for_report_kb, action_list
from states import AddShopState, CustomPeriodState
from utils import add_shop, get_all_user_shops, get_sales_report, check_shop_api, check_api_token, is_valid_date

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Выберите действие:", reply_markup=action_list)


@router.message(Command("addshop"))
async def add_shop_command(message: Message, state: FSMContext):
    await message.reply("Введите API-токен:")
    await state.set_state(AddShopState.add_shop_api)


@router.message(AddShopState.add_shop_api)
async def add_shop_api_token(message: Message, state: FSMContext):
    api_token = message.text
    msg = await message.reply("Проверка токена...")
    result = check_api_token(api_token)
    await msg.delete()

    if result is False:
        await message.answer("Неверный API-токен")
        await state.clear()
        return
    data = {
        'api_token': api_token,
        'telegram_id': message.from_user.id
    }
    check = check_shop_api(data)
    if check is False:
        await message.answer("Магазин с этим API-токеном уже добавлен")
        await state.clear()
        return
    await state.set_data(data)
    await message.reply("Введите имя магазина: ")
    await state.set_state(AddShopState.add_shop_name)


@router.message(AddShopState.add_shop_name)
async def add_shop_name(message: Message, state: FSMContext):
    shop_name = message.text

    data = await state.get_data()
    api_token = data['api_token']

    data = {
        'telegram_id': message.from_user.id,
        'api_token': api_token,
        'shop_name': shop_name
    }
    print(data)
    result = add_shop(data=data)
    if result:
        await message.answer("Магазин добавлен!")
    else:
        await message.answer("Магазин с таким названием уже добавлен")
    await state.clear()


@router.message(Command("delshop"))
async def delshop_command(message: Message):
    user_id = message.from_user.id
    shop_list = get_all_user_shops(user_id)
    if not shop_list:
        await message.answer("У вас нет добавленных магазинов")
        return
    await message.answer(f"Выберите магазин, которого хотите удалить:", reply_markup=get_shop_list_for_delete_kb(shop_list))


@router.message(Command("shops"))
async def shops_command(message: Message):
    user_id = message.from_user.id
    shop_list = get_all_user_shops(user_id)

    if not shop_list:
        await message.answer("У вас нет добавленных магазинов.")
        return

    shop_list_text = "\n".join([f"{i + 1}. <b>{item}</b>" for i, item in enumerate(shop_list)])

    await message.answer(f"Ваши магазины:\n{shop_list_text}", parse_mode="HTML")


@router.message(Command("report"))
async def report_command(message: Message):
    user_id = message.from_user.id
    shop_list = get_all_user_shops(user_id)
    if not shop_list:
        await message.answer("У вас нет добавленных магазинов.")
        return

    await message.answer("Выберите магазин: ", reply_markup=get_shop_list_for_report_kb(shop_list))


@router.message(CustomPeriodState.custom_period)
async def send_report_with_custom_period(message: Message, state: FSMContext):

    user_id = message.from_user.id
    try:
        date_from, date_to = message.text.split(" ", 1)
    except ValueError:
        await message.answer("Неверный формат даты. Дата должна быть в формате 'YYYY-MM-DD'")
        return

    if is_valid_date(date_from) and is_valid_date(date_to):
        msg = await message.answer("Высчитываем отчет...")

        date_from += "T00:00:00"
        date_to += "T23:59:59"

        shop_name = await state.get_data()
        result = get_sales_report(user_id, shop_name['shop_name'], date_from, date_to)
        await state.clear()
        await msg.delete()

        if not result:
            await message.answer("Произошла ошибка при получении отчета")
            return
        for item in result:
            try:
                await message.answer(item)
            except Exception as e:
                await message.answer(f"Произошла ошибка при отправки сообщения: {e}")

    else:
        await message.answer("Неверный формат даты. Дата должна быть в формате 'YYYY-MM-DD'")


@router.message(Command("help"))
async def help_command(message: Message):
    help_text = """
    <b>Доступные команды:</b>

    /start - Начало работы с ботом, выбор действия.
    /addshop - Добавить магазин с помощью API-токена.
    /delshop - Удалить магазин из списка.
    /shops - Показать список добавленных магазинов.
    /report - Получить отчет по продажам за выбранный период.
    /help - Показать это сообщение с описанием доступных команд.

    <b>Как использовать:</b>
    Для добавления магазина используйте команду <code>/addshop</code> и следуйте инструкциям.
    Чтобы удалить магазин, используйте <code>/delshop</code>.
    Для получения отчета по продажам, выберите <code>/report</code> и следуйте инструкциям для выбора магазина и периода.
    """
    await message.answer(help_text)
