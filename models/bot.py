import telegram   

from configs import BOT_TOKEN, CHAT_ID

async def bot_send_message(msg=''): 
    bot = telegram.Bot(token = BOT_TOKEN)
    async with bot:
        await bot.send_message(text=msg, chat_id=CHAT_ID)
