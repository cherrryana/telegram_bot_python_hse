import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, HELP_TEXT, MSG_NO_PROFILE
from utils import User, get_food_info, get_weather, users

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()


class FoodStates(StatesGroup):
    waiting_for_weight = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот, который поможет тебе следить за водой и калориями!\n\n"
        "Сначала давай настроим твой профиль: /set_profile"
        "Список всех команд: /help"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT)


@dp.message(Command("stop"))
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await message.answer("Вроде и так ничего не настраиваем...")

    await state.clear()
    await message.answer("Окей, прервали")


@dp.message(Command("set_profile"))
async def set_profile(message: types.Message, state: FSMContext):
    await message.answer("Отлично! Просто отвечай на мои вопросы, для начала - твой вес (кг)?")
    await state.set_state(ProfileStates.weight)


@dp.message(ProfileStates.weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        await state.update_data(weight=float(message.text))
        await message.answer("Теперь твой рост (см)?")
        await state.set_state(ProfileStates.height)
    except ValueError:
        await message.answer("Пожалуйста, введи свой вес числом (например, 75 или 70.5)")


@dp.message(ProfileStates.height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        await state.update_data(height=float(message.text))
        await message.answer("Сколько тебе лет?")
        await state.set_state(ProfileStates.age)
    except ValueError:
        await message.answer("Пожалуйста, введи свой рост числом (например, 175 или 170.5)")


@dp.message(ProfileStates.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        await state.update_data(age=int(message.text))
        await message.answer(
            "Сколько минут в день (примерно) ты активен? (прогулки, зал - всё считается)"
        )
        await state.set_state(ProfileStates.activity)
    except ValueError:
        await message.answer("Пожалуйста, введи свой возраст числом (например, 20)")


@dp.message(ProfileStates.activity)
async def process_activity(message: types.Message, state: FSMContext):
    try:
        await state.update_data(activity=int(message.text))
        await message.answer(
            "И последнее - в каком городе ты находишься?\n"
            "(я посмотрю погоду, это поможет мне рассчитать норму воды)"
        )
        await state.set_state(ProfileStates.city)
    except ValueError:
        await message.answer("Пожалуйста, введи время числом (например, 20)")


@dp.message(ProfileStates.city)
async def process_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    users[message.from_user.id] = User(
        weight=data["weight"],
        height=data["height"],
        age=data["age"],
        activity=data["activity"],
        city=message.text,
    )
    await message.answer(
        "Ура, профиль настроен!\n\n"
        "Можешь начинать вносить данные, вот несколько примеров доступных команд:\n\n"
        "- `/log_water 250`\n"
        "- `/log_food макароны`\n"
        "- `/log_workout бег 30`\n"
        "- `/check_progress`\n\n"
        "Список всех команд: /help\n\n"
        "Если что-то в процессе пойдет не так - просто напиши /stop или /cancel",
        parse_mode="Markdown",
    )
    await state.clear()


@dp.message(Command("log_water"))
async def log_water(message: types.Message):
    user = users.get(message.from_user.id)
    if not user:
        return await message.answer(MSG_NO_PROFILE)

    amount = int(message.text.split()[1]) if len(message.text.split()) > 1 else 0
    user.logged_water += amount
    temp = await get_weather(user.city)
    goal = user.calculate_water_goal(temp)
    await message.answer(
        f"Записано {amount} мл. Осталось выпить всего {max(0, int(goal - user.logged_water))} мл!"
    )


@dp.message(Command("log_food"))
async def log_food(message: types.Message, state: FSMContext):
    user = users.get(message.from_user.id)
    if not user:
        return await message.answer(MSG_NO_PROFILE)

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Вот пример запроса: /log_food яблоко")

    info = await get_food_info(parts[1])
    if info:
        await state.update_data(t_name=info["name"], t_cal=info["calories"])
        await message.answer(
            f"{info['name']} - {info['calories']} ккал на 100г. Сколько грамм ты съел?"
        )
        await state.set_state(FoodStates.waiting_for_weight)
    else:
        await message.answer("Продукт не найден :(")


@dp.message(FoodStates.waiting_for_weight)
async def process_food_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пожалуйста, введи только число (граммы)")

    weight = float(message.text)
    data = await state.get_data()
    user = users.get(message.from_user.id)

    total_cal = (data["t_cal"] * weight) / 100
    user.logged_calories += total_cal

    await message.answer(
        f"Отлично, записал {data['t_name']} {weight}г - это {total_cal:.1f} ккал!",
    )
    await state.clear()


@dp.message(Command("log_workout"))
async def log_workout(message: types.Message):
    user = users.get(message.from_user.id)
    if not user:
        return await message.answer(MSG_NO_PROFILE)

    parts = message.text.split()
    if len(parts) < 3:
        return await message.answer("Пример: /log_workout бег 30")

    mins = int(parts[2])
    burned = mins * 10  # условно 10 ккал/мин
    user.burned_calories += burned

    temp = await get_weather(user.city)
    goal = user.calculate_water_goal(temp)

    await message.answer(
        f"{parts[1]} {mins} мин - это примерно {burned} ккал!\n"
        "Продолжай в том же духе!\n\n"
        f"И не забывай пить воду: впереди еще {max(0, int(goal - user.logged_water))} мл воды!"
    )


@dp.message(Command("check_progress"))
async def check_progress(message: types.Message):
    user = users.get(message.from_user.id)
    if not user:
        return await message.answer(MSG_NO_PROFILE)

    temp = await get_weather(user.city)
    w_goal = user.calculate_water_goal(temp)
    c_goal = user.calculate_calorie_goal()

    text = (
        f"<b>Прогресс на сегодня:</b>\n\n"
        f"<b>Вода:</b>\n"
        f"- Выпито: {user.logged_water} мл из {int(w_goal)} мл\n"
        f"- Осталось: {max(0, int(w_goal - user.logged_water))} мл\n\n"
        f"<b>Калории:</b>\n"
        f"- Съедено: {user.logged_calories:.0f} ккал из {int(c_goal)} ккал\n"
        f"- Сожжено: {user.burned_calories} ккал\n"
        f"- Итого: {user.logged_calories - user.burned_calories:.0f} ккал"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("reset_today"))
async def cmd_reset(message: types.Message):
    user = users.get(message.from_user.id)
    if user:
        user.logged_water = user.logged_calories = user.burned_calories = 0
        await message.answer("Счетчики воды и калорий обнулены!")
    else:
        await message.answer(MSG_NO_PROFILE)


@dp.message(Command("delete_profile"))
async def cmd_delete_profile(message: types.Message, state: FSMContext):
    if message.from_user.id in users:
        del users[message.from_user.id]
        await state.clear()
        await message.answer("Профиль удален!")
    else:
        await message.answer(MSG_NO_PROFILE)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
