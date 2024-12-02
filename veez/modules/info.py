
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

@Client.on_message(filters.command('info'))
async def info(client, message):
    user = message.from_user
    args = message.text.split()

    if len(args) == 1:  
        profile_pic = await client.get_user_profile_photos(user.id)
        profile_pic_url = profile_pic.photos[0].file_id if profile_pic.photos else None
        
        user_info = (
            f"**User Information for {user.mention}:**\n"
            f"**First Name:** {user.first_name}\n"
            f"**Username:** @{user.username if user.username else 'N/A'}\n"
            f"**User ID:** {user.id}\n"
            f"**Date of Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**Permalink:** t.me/{user.username if user.username else 'N/A'}\n"
            f"**Profile Picture:** {profile_pic_url if profile_pic_url else 'No profile picture available'}\n"
        )
        
        close_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("Close", callback_data="close_info")]
        ])
        
        await message.reply_text(
            user_info,
            reply_markup=close_button
        )
    
    elif len(args) == 2:  
        target_id = int(args[1])
        
        try:
            # If it's a user ID
            user_info = await client.get_users(target_id)
            profile_pic = await client.get_user_profile_photos(target_id)
            profile_pic_url = profile_pic.photos[0].file_id if profile_pic.photos else None
            
            user_info_message = (
                f"**User Information for {user_info.mention}:**\n"
                f"**First Name:** {user_info.first_name}\n"
                f"**Username:** @{user_info.username if user_info.username else 'N/A'}\n"
                f"**User ID:** {user_info.id}\n"
                f"**Date of Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"**Permalink:** t.me/{user_info.username if user_info.username else 'N/A'}\n"
                f"**Profile Picture:** {profile_pic_url if profile_pic_url else 'No profile picture available'}\n"
                f"**First Name Changed:** {user_info.first_name_changes}\n"
                f"**Username Changed:** {user_info.username_changes}"
            )
            
            await message.reply_text(
                user_info_message,
                reply_markup=close_button
            )
        
        except Exception as e:
            try:
                # If it's a group ID
                group_info = await client.get_chat(target_id)
                group_profile_pic = await client.get_chat_photo(target_id)
                group_profile_pic_url = group_profile_pic.file_id if group_profile_pic else None
                
                group_info_message = (
                    f"**Group Information:**\n"
                    f"**Group Title:** {group_info.title}\n"
                    f"**Group ID:** {group_info.id}\n"
                    f"**Permalink:** {group_info.username if group_info.username else 'N/A'}\n"
                    f"**Group Profile Picture:** {group_profile_pic_url if group_profile_pic_url else 'No profile picture available'}\n"
                )
                
                await message.reply_text(
                    group_info_message,
                    reply_markup=close_button
                )
            except Exception as e:
                await message.reply_text("Could not find information for the provided ID.")
    else:
        await message.reply_text("Usage: /info [user_id or group_id]")

@Client.on_callback_query(filters.regex("close_info"))
async def close_info(client, callback_query):
    await callback_query.message.delete()  

