from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, User, Chat
from datetime import datetime
import os
from config import BOT_USERNAME

def get_user_info(user: User):
    user_info = (
        f"<b>Mention:</b> {user.mention}\n"
        f"<b>Username:</b> @{user.username if user.username else 'N/A'}\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Profile Link:</b> <a href='tg://user?id={user.id}'>Click Here</a>\n"
        f"<b>First Name:</b> {user.first_name if user.first_name else 'N/A'}\n"
        f"<b>Last Seen:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    return user_info

def get_group_info(group: Chat):
    group_info = (
        f"<b>Group Title:</b> {group.title}\n"
        f"<b>Group ID:</b> <code>{group.id}</code>\n"
        f"<b>Group Permalink:</b> <a href='https://t.me/{group.username}'>Click Here</a>\n"
    )
    return group_info

@Client.on_message(filters.command("info"))
async def info_command(client: Client, message: Message):
    try:
        wait_message = await message.reply_text("Please wait, I am searching...")

        if len(message.text.split()) > 1:
            entity_id = int(message.text.split()[1])
            # Check if the entity is a user or group by fetching its type
            if entity_id < 0:  # It's a group ID
                group = await client.get_chat(entity_id)
                group_info = get_group_info(group) 
                await wait_message.edit_text("found... Uploading group information.")
                profile_pic = await client.download_media(group.photo.big_file_id) if group.photo else None
                reply_message = await message.reply_photo(photo=profile_pic, caption=group_info, parse_mode="HTML", reply_markup=close_button())
                if profile_pic:
                    os.remove(profile_pic)
            else:  # It's a user ID
                user = await client.get_users(entity_id)
                user_info = get_user_info(user)
                await wait_message.edit_text("User found... Uploading user information.")
                profile_pic = await client.download_media(user.photo.big_file_id) if user.photo else None
                reply_message = await message.reply_photo(photo=profile_pic, caption=user_info, parse_mode="HTML", reply_markup=close_button())
                if profile_pic:
                    os.remove(profile_pic)
        else:
            user_info = get_user_info(message.from_user)
            await wait_message.edit_text("User found... Uploading your information.")
            profile_pic = await client.download_media(message.from_user.photo.big_file_id) if message.from_user.photo else None
            reply_message = await message.reply_photo(photo=profile_pic, caption=user_info, parse_mode="HTML", reply_markup=close_button())
            if profile_pic:
                os.remove(profile_pic)
        await wait_message.delete()

    except ValueError:
        await message.reply_text("Invalid user or group ID. Please provide a valid numerical ID.")
    except Exception as e:
        print(e)
        await message.reply_text(f"Something went wrong: {e}")

def close_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Close", callback_data="close_info")]
    ])

@Client.on_callback_query(filters.regex("close_info"))
async def close_info(client: Client, callback_query):
    await callback_query.message.delete()
