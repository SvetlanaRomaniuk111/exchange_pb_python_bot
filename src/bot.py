import os
import time
from typing import Dict
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from src.api import PrivatBankAPI

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Константы
CURRENCY_CODES: Dict[str, str] = {
    "Доллар 🇺🇸": "USD",
    "Евро 🇪🇺": "EUR"
}


class PrivatBankBot:
    """Класс бота для отображения курсов валют Приватбанка"""
    
    def __init__(self, token: str):
        """
        Инициализация бота
        
        Args:
            token (str): Токен Telegram бота
        """
        self.bot = TeleBot(token)
        self.api = PrivatBankAPI()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков сообщений"""
        self.bot.message_handler(commands=["start"])(self.send_welcome)
        self.bot.message_handler(commands=["help"])(self.send_help)
        self.bot.message_handler(func=lambda message: message.text == "🔄 Обновить курсы")(self.refresh_rates)
        self.bot.message_handler(func=lambda message: message.text in CURRENCY_CODES.keys())(self.send_exchange_rate)
    
    def send_welcome(self, message):
        """Отправка приветственного сообщения с клавиатурой"""
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = [KeyboardButton(currency_name) for currency_name in CURRENCY_CODES.keys()]
        markup.add(*buttons)
        markup.add(KeyboardButton("🔄 Обновить курсы"))
        
        self.bot.send_message(
            message.chat.id, 
            "Выберите валюту, чтобы узнать курс к гривне (UAH):", 
            reply_markup=markup
        )
    
    def send_help(self, message):
        """Отправка справочной информации"""
        help_text = (
            "Этот бот показывает курсы валют Приватбанка к гривне (UAH).\n\n"
            "Команды:\n"
            "/start - показать клавиатуру с валютами\n"
            "/help - показать это сообщение\n\n"
            "Нажмите на название валюты, чтобы узнать её курс."
        )
        self.bot.send_message(message.chat.id, help_text)
    
    def refresh_rates(self, message):
        """Обновление курсов валют"""
        self.bot.send_message(message.chat.id, "Получение актуальных курсов...")
        self.send_welcome(message)
    
    def send_exchange_rate(self, message):
        """Отправка информации о курсе выбранной валюты"""
        currency_name = message.text
        currency_code = CURRENCY_CODES[currency_name]
        
        try:
            exchange_rates = self.api.get_exchange_rates()
            rate_info = next((rate for rate in exchange_rates if rate['ccy'] == currency_code), None)
            
            if rate_info:
                last_updated = time.strftime("%d.%m.%Y %H:%M:%S")
                buy_rate = float(rate_info['buy'])
                sell_rate = float(rate_info['sale'])
                
                response = (
                    f"💰 Курс {currency_name} в Приватбанке:\n\n"
                    f"🔹 Покупка: {buy_rate:.2f} UAH\n"
                    f"🔸 Продажа: {sell_rate:.2f} UAH\n\n"
                    f"⏱ Обновлено: {last_updated}"
                )
                self.bot.send_message(message.chat.id, response)
            else:
                self.bot.send_message(message.chat.id, f"Информация по валюте {currency_code} не найдена")
        except Exception as e:
            self.bot.send_message(message.chat.id, f"Ошибка при получении курса: {str(e)}")
    
    def run(self):
        """Запуск бота"""
        print("Бот запущен...")
        self.bot.remove_webhook()  # Удаляем webhook если он был установлен
        self.bot.infinity_polling(allowed_updates=None, skip_pending=True)


def main():
    """Точка входа в программу"""
    try:
        bot = PrivatBankBot(TOKEN)
        bot.run()
    except Exception as e:
        print(f"Критическая ошибка бота: {str(e)}")