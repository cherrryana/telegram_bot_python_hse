import os

from dotenv import load_dotenv

load_dotenv()

# access keys
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# urls
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
FOOD_SEARCH_URL = (
    "https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product}&json=true"
)

# default values
DEFAULT_TEMP = 20
WATER_PER_KG = 30
WATER_ACTIVITY_BONUS = 500
WATER_WEATHER_BONUS = 500
HOT_WEATHER_THRESHOLD = 25

CALORIES_WEIGHT_MULT = 10
CALORIES_HEIGHT_MULT = 6.25
CALORIES_AGE_MULT = 5
CALORIES_ACTIVITY_BASE = 200

MSG_NO_PROFILE = "Твой профиль еще не настроен!\nЧтобы создать его, просто напиши мне /set_profile"
HELP_TEXT = (
    "Список доступных команд:\n\n"
    "/set_profile - настроить параметры пользователя (вес, рост, возраст и т.д.)\n"
    "/log_water 250 - записать выпитую воду (в мл)\n"
    "/log_food яблоко - записать съеденный продукт\n"
    "/log_workout бег 30 - записать тренировку (тип и время в минутах)\n"
    "/check_progress - показать текущий прогресс по воде и калориям\n"
    "/reset_today - обнулить прогресс за текущий день\n"
    "/delete_profile - полностью и безвозвратно удалить профиль и данные\n"
    "/help - показать это сообщение"
)
