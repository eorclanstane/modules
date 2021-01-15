from .. import loader, utils
import logging

from telethon.tl.functions.users import GetFullUserRequest

logger = logging.getLogger(__name__)


@loader.tds
class UserInfoMod(loader.Module):
    """Рассказывает о людях"""
    strings = {"name": "О пользователе",
               "first_name": "Имя: <code>{}</code>",
               "last_name": "\nФамилия: <code>{}</code>",
               "id": "\nID: <code>{}</code>",
               "bio": "\nБио: <code>{}</code>",
               "restricted": "\nОграничен: <code>{}</code>",
               "deleted": "\nУдалён: <code>{}</code>",
               "bot": "\nБот: <code>{}</code>",
               "verified": "\nПодтверждён: <code>{}</code>",
               "dc_id": "\nДата-Центр ID: <code>{}</code>",
               "find_error": "<b>Не удалось найти этого пользователя.</b>",
               "no_args_or_reply": "<b>Никаких аргументов или ответа предоставлено не было.</b>",
               "provide_user": "Предоставьте пользователя для поиска информации",
               "searching_user": "Собираю информацию о пользователе...",
               "cannot_find": "Не могу найти пользователя.",
               "permalink_txt": "<a href='tg://user?id={uid}'>{txt}</a>",
               "permalink_uid": "<a href='tg://user?id={uid}'>Перма-линк: {uid}</a>",
               "encode_cfg_doc": "Кодировать символы Юникода"}

    def __init__(self):
        self.config = loader.ModuleConfig("ENCODE", False, lambda m: self.strings("encode_cfg_doc", m))

    def _handle_string(self, string):
        if self.config["ENCODE"]:
            return utils.escape_html(ascii(string))
        return utils.escape_html(string)

    @loader.unrestricted
    @loader.ratelimit
    async def userinfocmd(self, message):
        """Используйте в ответ, чтобы получить информацию о пользователе"""
        if message.is_reply:
            full = await self.client(GetFullUserRequest((await message.get_reply_message()).from_id))
        else:
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, self.strings("no_args_or_reply", message))
            try:
                full = await self.client(GetFullUserRequest(args[0]))
            except ValueError:
                return await utils.answer(message, self.strings("find_error", message))
        logger.debug(full)
        reply = self.strings("first_name", message).format(self._handle_string(full.user.first_name))
        if full.user.last_name is not None:
            reply += self.strings("last_name", message).format(self._handle_string(full.user.last_name))
        reply += self.strings("id", message).format(utils.escape_html(full.user.id))
        reply += self.strings("bio", message).format(self._handle_string(full.about))
        reply += self.strings("restricted", message).format(utils.escape_html(str(full.user.restricted)))
        reply += self.strings("deleted", message).format(utils.escape_html(str(full.user.deleted)))
        reply += self.strings("bot", message).format(utils.escape_html(str(full.user.bot)))
        reply += self.strings("verified", message).format(utils.escape_html(str(full.user.verified)))
        if full.user.photo:
            reply += self.strings("dc_id", message).format(utils.escape_html(str(full.user.photo.dc_id)))
        await utils.answer(message, reply)

    @loader.unrestricted
    @loader.ratelimit
    async def permalinkcmd(self, message):
        """Получить постоянную ссылку на пользователя на основе идентификатора или имени пользователя"""
        args = utils.get_args(message)
        if len(args) < 1:
            await utils.answer(message, self.strings("provide_user", message))
            return
        try:
            user = int(args[0])
        except ValueError:
            user = args[0]
        try:
            user = await self.client.get_entity(user)
        except ValueError as e:
            logger.debug(e)
            # look for the user
            await utils.answer(message, self.strings("searching_user", message))
            await self.client.get_dialogs()
            try:
                user = await self.client.get_entity(user)
            except ValueError:
                await utils.answer(message, self.strings("cannot_find", message))
                return
        if len(args) > 1:
            await utils.answer(message, self.strings("permalink_txt", message).format(uid=user.id, txt=args[1]))
        else:
            await utils.answer(message, self.strings("permalink_uid", message).format(uid=user.id))

    async def client_ready(self, client, db):
        self.client = client