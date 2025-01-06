from aiogram.fsm.state import StatesGroup, State


class AddShopState(StatesGroup):
    add_shop_name = State()
    add_shop_api = State()


class CustomPeriodState(StatesGroup):
    custom_period = State()
