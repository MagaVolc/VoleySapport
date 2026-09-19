from telebot import types

def main_menu() -> types.InlineKeyboardMarkup:
  kb = types.InlineKeyboardMarkup(row_width=2)
  kb.add(types.InlineKeyboardButton("🏐 Задать вопрос", callback_data="ask"))
  kb.add(
      types.InlineKeyboardButton("👤 Профиль", callback_data="profile"),
      types.InlineKeyboardButton("ℹ️ О нас", callback_data="about"),
  )
  kb.add(
      types.InlineKeyboardButton("🎁 Промокод", callback_data="promo"),
      types.InlineKeyboardButton("🆘 Тех. поддержка", callback_data="support"),
  )
  return kb