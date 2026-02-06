import aiohttp

import config

users = {}


class User:
    def __init__(self, weight, height, age, activity, city):
        self.weight = weight
        self.height = height
        self.age = age
        self.activity = activity
        self.city = city
        self.logged_water = 0
        self.logged_calories = 0
        self.burned_calories = 0

    def calculate_water_goal(self, temp):
        base = self.weight * config.WATER_PER_KG
        activity_bonus = (self.activity // 30) * config.WATER_ACTIVITY_BONUS
        weather_bonus = config.WATER_WEATHER_BONUS if temp > config.HOT_WEATHER_THRESHOLD else 0
        return base + activity_bonus + weather_bonus

    def calculate_calorie_goal(self):
        base = (
            config.CALORIES_WEIGHT_MULT * self.weight
            + config.CALORIES_HEIGHT_MULT * self.height
            - config.CALORIES_AGE_MULT * self.age
        )
        return base + (config.CALORIES_ACTIVITY_BASE if self.activity > 0 else 0)


async def get_weather(city):
    url = config.WEATHER_URL.format(city=city, api_key=config.WEATHER_API_KEY)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                return data["main"]["temp"]
        except:
            return config.DEFAULT_TEMP


async def get_food_info(product_name):
    url = config.FOOD_SEARCH_URL.format(product=product_name)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            products = data.get("products", [])
            if products:
                p = products[0]
                return {
                    "name": p.get("product_name", product_name),
                    "calories": p.get("nutriments", {}).get("energy-kcal_100g", 0),
                }
    return None
