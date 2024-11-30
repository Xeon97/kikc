
from telethon import events
from datetime import datetime, timedelta

from .. import loader, utils


@loader.tds
class KickInactiveMod(loader.Module):
    """Кикает пользователей, которые не писали в чат указанное количество дней"""

    strings = {"name": "KickInactive"}

    # Список разрешенных чатов
    ALLOWED_CHATS = [-1001234567890, -1009876543210]  # Замените на ID ваших чатов

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def kikat(self, message):
        """Использование: %kikat <количество дней>"""
        chat = await message.get_chat()
        
        # Проверка, разрешен ли чат
        if chat.id not in self.ALLOWED_CHATS:
            await message.edit("Эта команда недоступна в этом чате.")
            return

        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            await message.edit("Введите количество дней: %kikat <дни>")
            return

        days = int(args)
        await message.edit(f"Проверяю пользователей, которые не писали в чат {days} дней...")
        threshold_date = datetime.now() - timedelta(days=days)
        kicked = 0

        async for user in self.client.iter_participants(chat.id):
            if user.bot or user.deleted:
                continue

            async for msg in self.client.iter_messages(chat.id, from_user=user.id, limit=1):
                if msg.date and msg.date >= threshold_date:
                    break
            else:
                try:
                    await self.client.kick_participant(chat.id, user.id)
                    kicked += 1
                except Exception as e:
                    await message.reply(f"Не удалось кикнуть {user.id}: {e}")

        await message.edit(f"Кикнуто пользователей: {kicked}.")
