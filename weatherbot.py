import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация
BOT_TOKEN = ""  # Замените на реальный токен
OWM_API_KEY = ""  # Ваш API-ключ

def get_weather(city: str) -> str:
    """Запрашивает погоду через OpenWeatherMap API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()
        
        if data.get("cod") != 200:
            return "❌ Город не найден. Проверьте название."
            
        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        country = data.get("sys", {}).get("country", "не указана")  # Получаем код страны
        
        # Добавляем флаг страны (необязательно)
        country_flags = {
            "RU": "🇷🇺", "US": "🇺🇸", "DE": "🇩🇪", "FR": "🇫🇷", 
            "IT": "🇮🇹", "ES": "🇪🇸", "GB": "🇬🇧", "JP": "🇯🇵",
            "TJ": "🇹🇯", "UZ": "🇺🇿", "KG": "🇰🇬", "KZ": "🇰🇿"
        }
        flag = country_flags.get(country, "🌐")
        
        return (
            f"📍 {data['name']}, {flag}{country}\n"
            f"🌤 Погода в {city}:\n"
            f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"☁️ Состояние: {weather}\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌬 Ветер: {wind} м/с"
        )
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот погоды. Напиши мне название города, например: Канибадам"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    city = update.message.text
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

async def run_bot():
    """Запускает и поддерживает работу бота"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот успешно запущен!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Ожидаем завершения
    try:
        while True:
            await asyncio.sleep(3600)  # Проверка каждые 3600 секунд (1 час)
    except asyncio.CancelledError:
        print("Получен сигнал завершения...")
    finally:
        print("Остановка бота...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Бот остановлен по запросу пользователя")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
