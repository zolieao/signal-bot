import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keys import TOKEN, URL, chatID 



async def send_signal_to_telegram(signal, elem):
    
    bot = telegram.Bot(token=TOKEN)
    
    message = f"Сигнал: {signal} для {elem}"
    await bot.send_message(chat_id=chatID, text=message)

