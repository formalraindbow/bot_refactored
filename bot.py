from handlers import bot
from telebot import custom_filters


bot.add_custom_filter(custom_filters.StateFilter(bot))

# Запускаем бота
if __name__ == "__main__":
    bot.infinity_polling()
