import telebot
import config
import json
from datetime import datetime
from sistema.keyboard import *
from sistema.quest import *
import logging
from logging.handlers import RotatingFileHandler


handler = RotatingFileHandler(
    "data/bot.log",
    maxBytes=10 * 1024 * 1024,  # 10 МБ
    backupCount=3,
    encoding="utf-8",
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[handler, logging.StreamHandler()],
)
log = logging.getLogger(__name__)

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def start(message):
  user = message.chat.id
  log.info(f"{user} использовал /start")
  with open('data/users.json', 'r') as file:
    data = json.load(file)
    if not user in data:
      log.info(f"Новый юзер: {user}")
      data[str(user)] = {
        'id': message.chat.id,
        'data_reg': datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S"),
        'sub': False,
        'sub_until': None,
        'last_pay': None,
        'ban': False,
        'free_quest' : 3, #количество бесплатных/реф запросов
        'limit' : 0,
      }
      with open('data/users.json', 'w') as f:
        json.dump(data, f, indent=2)
  bot.send_message(
      message.chat.id,
      f"🏐 Привет, {message.from_user.first_name}!\n\n"
      "Я — бот-помощник по правилам волейбола.\n"
      "Отвечаю по официальным правилам ФИВБ/ВФВ редакции 2025–2028.\n\n"
      "Задавай вопрос — отвечу развёрнуто, со ссылками на пункты правил.\n\n"
      "Примеры:\n"
      "• Может ли либеро касаться сетки?\n"
      "• Сколько касаний разрешено команде?\n"
      "• Что считается блоком?\n\n"
      "⚠️ Важно: каждое сообщение, кроме команд, воспринимается как запрос "
      "и списывается из дневного лимита. Не флуди — сначала подумай, потом пиши."
  )



@bot.message_handler(content_types=["text"])
def on_question(message):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    # не текст
    if not text:
        return

    # команда
    if text.startswith("/"):
        return

    # слишком длинно
    if len(text) > 100:
        bot.send_message(user_id, "Слишком длинный вопрос. Сократи до 100 символов.")
        return
    log.info(f"Вопрос от {user_id}: {text[:80]}")
    with open('data/users.json') as f:
        file = json.load(f)
        if file[str(user_id)]['free_quest'] < 5:
            bot.send_message(user_id, 'У вас кончились запросы! Обратитесь к разработчику за выдачей новых/купите подписку!')
        if not file[str(user_id)]['free_quest'] == 0:
            file[str(user_id)]['limit'] += 1
            file[str(user_id)]['free_quest'] -= 1
            with open('data/users.json', 'w') as fr:
                json.dump(file, fr, indent=4)
    msg = bot.send_message(user_id, "⏳ Ищу ответ...")
    answer = ask_ai(text)
    log.info(f"Ответ отправлен {user_id}, длина {len(answer)}")
    bot.edit_message_text(answer, user_id, msg.message_id, parse_mode='Markdown')

  
print('Я запустился')
log.info(f"Бот запущен!")
bot.infinity_polling(none_stop=True)