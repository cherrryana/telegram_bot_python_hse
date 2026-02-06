# Telegram-бот для трекинга калорий и выпитой воды

## Установка и запуск

1. Клонируем репозитрий:
    ```bash
    git clone https://github.com/username/project-name.git
    ```

2. Устанавливаем зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. Создаем файл .env в корне и прописываем параметры:
   BOT_TOKEN=ваш_токен_бота
   WEATHER_API_KEY=ваш_ключ_openweathermap

4. Запускаем приложение!
    ```bash
    python bot.py
    ```

## Список команд
- /set_profile - настройка параметров пользователя и расчет норм
- /log_water [объем] - запись потребления воды (мл)
- /log_food [название] - поиск и запись калорийности продукта
- /log_workout [тип] [время] - запись тренировки
- /check_progress - вывод текущей статистики за день
- /stop или /cancel - прерывание любого активного процесса
- /delete_profile - полное удаление профиля
- /reset_today
