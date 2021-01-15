import logging
import platform
import asyncio
import shutil
import sys

import telethon

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class InfoMod(loader.Module):
    """Предоставляет системную информацию о компьютере, на котором размещен этот бот"""
    strings = {"name": "O системе",
               "info_title": "<b>Информация о системе</b>",
               "kernel": "<b>Ядро:</b> <code>{}</code>",
               "arch": "<b>Архитектура:</b> <code>{}</code>",
               "os": "<b>Операционная система:</b> <code>{}</code>",
               "distro": "<b>Дистрибутив Linux:</b> <code>{}</code>",
               "android_sdk": "<b>Android SDK:</b> <code>{}</code>",
               "android_ver": "<b>Версия Android:</b> <code>{}</code>",
               "android_patch": "<b>Патч безопасности Android:</b> <code>{}</code>",
               "unknown_distro": "<b>Не могу определить дистрибутив Linux.</b>",
               "python_version": "<b>Версия Python:</b> <code>{}</code>",
               "telethon_version": "<b>Версия Telethon:</b> <code>{}</code>"}

    async def infocmd(self, message):
        """Показывает системную информацию"""
        reply = self.strings("info_title", message)
        reply += "\n" + self.strings("kernel", message).format(utils.escape_html(platform.release()))
        reply += "\n" + self.strings("arch", message).format(utils.escape_html(platform.architecture()[0]))
        reply += "\n" + self.strings("os", message).format(utils.escape_html(platform.system()))

        if platform.system() == "Linux":
            done = False
            try:
                a = open("/etc/os-release").readlines()
                b = {}
                for line in a:
                    b[line.split("=")[0]] = line.split("=")[1].strip().strip("\"")
                reply += "\n" + self.strings("distro", message).format(utils.escape_html(b["PRETTY_NAME"]))
                done = True
            except FileNotFoundError:
                getprop = shutil.which("getprop")
                if getprop is not None:
                    sdk = await asyncio.create_subprocess_exec(getprop, "ro.build.version.sdk",
                                                               stdout=asyncio.subprocess.PIPE)
                    ver = await asyncio.create_subprocess_exec(getprop, "ro.build.version.release",
                                                               stdout=asyncio.subprocess.PIPE)
                    sec = await asyncio.create_subprocess_exec(getprop, "ro.build.version.security_patch",
                                                               stdout=asyncio.subprocess.PIPE)
                    sdks, unused = await sdk.communicate()
                    vers, unused = await ver.communicate()
                    secs, unused = await sec.communicate()
                    if sdk.returncode == 0 and ver.returncode == 0 and sec.returncode == 0:
                        reply += "\n" + self.strings("android_sdk", message).format(sdks.decode("utf-8").strip())
                        reply += "\n" + self.strings("android_ver", message).format(vers.decode("utf-8").strip())
                        reply += "\n" + self.strings("android_patch", message).format(secs.decode("utf-8").strip())
                        done = True
            if not done:
                reply += "\n" + self.strings("unknown_distro", message)
        reply += "\n" + self.strings("python_version", message).format(utils.escape_html(sys.version))
        reply += "\n" + self.strings("telethon_version", message).format(utils.escape_html(telethon.__version__))
        await utils.answer(message, reply)