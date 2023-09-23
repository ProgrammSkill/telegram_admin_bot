from datetime import datetime, timedelta
from db import BotDB
from dispatcher import dp, bot
from aiogram import types
import logging
import config

db = BotDB('admin_bot_db.db')
logging.basicConfig(level=logging.INFO)

ALLOWED_CHAT_IDS = ['идентификатор_чата1', 'идентификатор_чата2']

async def get_user_status(chat: types.Chat, user_id: int):
    chat_member = await chat.get_member(user_id)
    return chat_member.status

async def restrict_user(chat: types.Chat, user_id: int):
    await chat.restrict(user_id, can_send_messages=False)


def handle_message(update):
    chat_id = update['message']['chat']['id']
    if str(chat_id) != str(config.GROUP_ID):
        return


@dp.message_handler(commands=['start', 'старт'], commands_prefix='./!')
async def start(message: types.Message):
    chat_id = message.chat.id
    print(chat_id)
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    await message.reply("Привет! Я полиция Лиц Питера. Напиши /help или /помощь, чтобы узнать, что я умею.")


@dp.message_handler(commands=['help', 'помощь'], commands_prefix='./!')
async def start(message: types.Message):
    chat_id = message.chat.id
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    await message.reply("Инструкция по боту: https://docs.google.com/document/d/1md58RJSkcDzZSM4Y_vfjLn8f4uHfIc9cZHApuf5ytmw/edit?usp=sharing", parse_mode='html')


@dp.message_handler(commands=['upgrade', 'повысить'], commands_prefix='./!', is_chat_admin=True)
async def raise_level(message):
    chat_id = message.chat.id
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    if not message.reply_to_message:
        await message.reply("🚫 Эта команда должна быть ответом на сообщение!", parse_mode='html')
        return
    chat = message.chat
    user_id = message.from_user.id
    user_status = await get_user_status(chat, user_id)
    if user_status == 'creator' or (user_status == 'administrator' and db.check_level(user_id) >= 2):
        id_user_to = message.reply_to_message.from_user.id
        user_status = await get_user_status(chat, id_user_to)
        if user_status == 'creator' or user_status == 'administrator':
            try:
                level = int(message.text.split()[1])
            except:
                level = int(db.check_level(id_user_to)) + 1

            if not level > 2:
                if db.check_user(id_user_to) != True:
                    db.add_user(id_user_to, level)
                else:
                    db.change_level(id_user_to, level)
                await message.reply(f'✅ <a href="tg://user?id={id_user_to}">{message.reply_to_message.from_user.full_name}</a> назначен администратором уровня {level}', parse_mode='html')
            else:
                await message.reply(f'🚫 Максимальный уровень 2')
        else:
            await message.reply(f'🚫 Гражданин не является администратором чата, я не могу выдать ему права')
    else:
        await message.reply('🚫 У Вас нет прав для этой команды. Требуется уровень 2', parse_mode='html')


@dp.message_handler(commands=['downgrade', 'понизить'], commands_prefix='./!', is_chat_admin=True)
async def downgrade(message):
    chat_id = message.chat.id
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    if not message.reply_to_message:
        await message.reply("🚫 Эта команда должна быть ответом на сообщение!")
        return
    chat = message.chat
    user_id = message.from_user.id
    user_status = await get_user_status(chat, user_id)
    if user_status == 'creator' or (user_status == 'administrator' and db.check_level(user_id) >= 2):
        id_user_to = message.reply_to_message.from_user.id
        user_status = await get_user_status(chat, id_user_to)
        if user_status != 'creator' or (db.check_level(user_id) < 2):
            try:
                level = int(message.text.split()[1])
            except:
                level = int(db.check_level(id_user_to)) - 1

            if db.check_user(id_user_to) == True:
                if int(db.check_level(id_user_to)) == 1:
                    db.delete_user(id_user_to)
                    await message.reply(
                        f'✅ У пользователя <a href="tg://user?id={id_user_to}">{message.reply_to_message.from_user.first_name}</a> сняты все права',
                        parse_mode='html')
                else:
                    db.change_level(id_user_to, level)
                    level = int(db.check_level(id_user_to))
                    await message.reply(
                        f'✅ Администратор <a href="tg://user?id={id_user_to}">{message.reply_to_message.from_user.first_name}</a> был понижен до уровня {level}',
                        parse_mode='html')
            else:
                await message.reply(
                    f'У пользователя <a href="tg://user?id={id_user_to}">{message.reply_to_message.from_user.first_name}</a> ранее не было прав',
                    parse_mode='html')
    else:
        await message.reply('🚫 У Вас нет прав для этой команды. Требуется уровень 2', parse_mode='html')


@dp.message_handler(commands=['снять', 'demote'], commands_prefix='./!', is_chat_admin=True)
async def remove_all_rights(message):
    chat_id = message.chat.id
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    if not message.reply_to_message:
        await message.reply("🚫 Эта команда должна быть ответом на сообщение!")
        return

    chat = message.chat
    user_id = message.from_user.id
    user_status = await get_user_status(chat, user_id)
    if user_status == 'creator' or (user_status == 'administrator' and db.check_level(user_id) >= 2):
        id_user_to = message.reply_to_message.from_user.id
        user_status = await get_user_status(chat, id_user_to)
        if user_status != 'creator' or (db.check_level(user_id) < 2):
            if db.check_user(id_user_to) == True:
                db.delete_user(id_user_to)
                await message.reply(f'✅ У пользователя <a href="tg://user?id={id_user_to}">{message.reply_to_message.from_user.first_name}</a> сняты все права', parse_mode='html')
            else:
                await message.reply(f'У пользователя <a href="tg://user?id={id_user_to}">{message.reply_to_message.from_user.first_name}</a> ранее не было прав', parse_mode='html')
    else:
        await message.reply('🚫 У Вас нет прав для этой команды. Требуется уровень 2', parse_mode='html')


@dp.message_handler(commands=['mute', 'мут', 'арест', 'арестовать'], commands_prefix='./!', is_chat_admin=True)
async def mute(message):
    chat_id = message.chat.id
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    name = message.from_user.get_mention(as_html=True)

    image_path = "./image/ban.jpg"
    image = types.InputFile(image_path)

    if not message.reply_to_message:
     await message.reply("Эта команда должна быть ответом на сообщение!")
     return

    chat = message.chat
    user_id = message.from_user.id
    user_status = await get_user_status(chat, user_id)
    if user_status == 'creator' or (user_status == 'administrator' and db.check_level(user_id) >= 1):
      try:
         muteint = int(message.text.split()[1])
         mutetype = message.text.split()[2]
         comment = " ".join(message.text.split()[3:])
      except IndexError:
         await message.reply('Не хватает аргументов!\nПример:\n`/мут 1 ч причина`')
         return

      user_status = await get_user_status(chat, user_id)
      if user_status != 'creator' or user_status != 'administrator':
          if mutetype == "ч" or mutetype == "часов" or mutetype == "час" or mutetype == "часа":
            dt = datetime.now() + timedelta(hours=muteint)
            timestamp = dt.timestamp()
            try:
                await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=timestamp)
                await bot.send_photo(chat_id=message.chat.id, photo=image, caption=f' | <b>Решение было принято:</b> {name}\n | <b>Нарушитель закона:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a>\n⏰ | <b>Срок наказания:</b> {muteint} {mutetype}\n | <b>Причина:</b> {comment}',  parse_mode='html')
            except Exception as e:
                if str(e) == 'Not enough rights to restrict/unrestrict chat member':
                    await message.reply('У меня нет полномочий на мут')
          elif mutetype == "м" or mutetype == "минут" or mutetype == "минуты":
             dt = datetime.now() + timedelta(minutes=muteint)
             timestamp = dt.timestamp()
             try:
                await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=timestamp)
                await bot.send_photo(chat_id=message.chat.id, photo=image, caption=f' | <b>Решение было принято:</b> {name}\n | <b>Нарушитель закона:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a>\n⏰ | <b>Срок наказания:</b> {muteint} {mutetype}\n | <b>Причина:</b> {comment}',  parse_mode='html')
             except Exception as e:
                 if str(e) == 'Not enough rights to restrict/unrestrict chat member':
                    await message.reply('У меня нет полномочий на мут')
          elif mutetype == "д" or mutetype == "дней" or mutetype == "день" or mutetype == "дня":
             dt = datetime.now() + timedelta(days=muteint)
             timestamp = dt.timestamp()
             try:
                await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, types.ChatPermissions(False), until_date=timestamp)
                await bot.send_photo(chat_id=message.chat.id, photo=image, caption=f' | <b>Решение было принято:</b> {name}\n | <b>Нарушитель закона:</b> <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a>\n⏰ | <b>Срок наказания:</b> {muteint} {mutetype}\n | <b>Причина:</b> {comment}',  parse_mode='html')
             except Exception as e:
                if str(e) == 'Not enough rights to restrict/unrestrict chat member':
                    await message.reply('У меня нет полномочий на мут')
      else:
          await message.reply('Я не могу арестовать администратора')
    else:
      await message.reply('🚫 У Вас нет прав для этой команды. Требуется уровень 2', parse_mode='html')


@dp.message_handler(commands=['structure', 'состав'], commands_prefix='./!')
async def send_records(message: types.Message):
    chat_id = message.chat.id
    if str(chat_id) != str(config.GROUP_ID):
        await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
        return

    records = db.list_administrators()
    text = 'Администраторы:\n\n'
    count = 1
    for record in records:
        try:
            chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=record[1])
            user_name = chat_member.user.full_name
            text += f'{count}. <a href="tg://user?id={record[1]}">{user_name}</a>, уровень - {record[2]}\n'
        except:
            pass
        count = count + 1
    await bot.send_message(chat_id=message.chat.id, text=text, parse_mode='html')


forbidden_words = ['впишу девушку', 'впишу девушек', 'впишем девушек', 'впишем девушку', 'впишу девушку',\
'угостит мяу', 'угостите мяу', 'скиньте деньги', 'пара мж пригласит', 'кто накурит', 'впишем парня', 'впишем парней',\
'впишем девушку', 'доставка мяу', 'впишу за мп', 'впишу адекватную', 'впишем красивую', 'ищу девушку мп', 'мы пара ж',\
'мы пара м', 'впишусь за мп', 'впишусь покурить альфу', 'впишит пару', 'есть мяу', 'приглашу девушку', 'приглашу парня',\
'впишем девушек', 'впишите на мяу', 'встречусь с парнем', 'впишу или впишусь', 'угощу гашем', 'впишу на мефедрон',\
'мяу есть', 'есть мяу', 'покурить шишек', 'впишусь к девушке', 'впишемся на мяу', 'впишем того кто угостит мяу',\
'встречусь с девушкой', 'парень и 2 девушки впишемся', 'альфа пвп', 'впишу на меф', 'впишем на меф', 'впишусь на меф',
'приглашаю девушку', 'приеду в гости за мп', 'приеду в гости, за мп', 'встречусь с мужчиной за мп',\
'встречусь с мужчиной в авто за мп', 'впишу сейчас к себе', 'мефедрон', 'впишу за мяу']


@dp.message_handler()
async def deleting_messages(message: types.Message):
    text = message.text.lower()
    user_id = message.from_user.id
    name = message.from_user.full_name
    for i in forbidden_words:
        if i in text:
            chat_id = message.chat.id
            if str(chat_id) != str(config.GROUP_ID):
                await bot.send_message(chat_id, 'Я работаю только в Лицах Питера https://t.me/FacesPeterburg')
                return
            await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            await bot.send_message(chat_id=chat_id,
                text=f'<a href="tg://user?id={user_id}">{name}</a>, ваше сообщение было удаленно, поскольку подобное сообщение противоречит законам Лиц Питера',
                parse_mode='html')
            break
