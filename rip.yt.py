import os
import time
import asyncio
import shutil
from bs4 import BeautifulSoup
import re
from html import unescape
from requests import get

from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, YOUTUBE_API_KEY, CHROME_DRIVER, GOOGLE_CHROME_BIN
from userbot.events import register
from telethon.tl.types import DocumentAttributeAudio
from uniborg.util import progress, humanbytes, time_formatter


@register(outgoing=True, pattern=r".rip (audio|video) (.*)")
async def download_video(v_url):
    """ .rip - загружайте медиафайлы с YouTube и многих других сайтов.. """
    url = v_url.pattern_match.group(2)
    type = v_url.pattern_match.group(1).lower()
    reply = await v_url.get_reply_message()
    await v_url.edit("`Подготовка к загрузке...`")

    if type == "audio":
        opts = {
            'format':
            'bestaudio',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'writethumbnail':
            True,
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl':
            '%(id)s.mp3',
            'quiet':
            True,
            'logtostderr':
            False
        }
        video = False
        song = True

    elif type == "video":
        opts = {
            'format':
            'best',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl':
            '%(id)s.mp4',
            'logtostderr':
            False,
            'quiet':
            True
        }
        song = False
        video = True

    try:
        await v_url.edit("`Получаем данные, жди...`")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        await v_url.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await v_url.edit("`Загружаемый контент слишком мелкий.`")
        return
    except GeoRestrictedError:
        await v_url.edit(
            "`Видео недоступно для вашего географического местоположения из-за географических ограничений, установленных веб-сайтом..`"
        )
        return
    except MaxDownloadsReached:
        await v_url.edit("`Лимит загрузок такой: \"оп ахах\".`")
        return
    except PostProcessingError:
        await v_url.edit("`Ошибка в пост-процессинге.`")
        return
    except UnavailableVideoError:
        await v_url.edit("`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await v_url.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await v_url.edit("`Ошибка при экспорте видео.`")
        return
    except Exception as e:
        await v_url.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    if song:
        u = rip_data['uploader'] if 'uploader' in rip_data else 'Northing'
        await v_url.edit(f"`Загружаю аудио:`\
        \n**{rip_data['title']}**\
        \nby *{u}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp3",
            supports_streaming=True,
            reply_to=reply.id if reply else None,
            attributes=[
                DocumentAttributeAudio(duration=int(rip_data['duration']),
                                       title=str(rip_data['title']),
                                       performer=u)
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Загружаю..",
                         f"{rip_data['title']}.mp3")))
        os.remove(f"{rip_data['id']}.mp3")
        await v_url.delete()
    elif video:
        u = rip_data['uploader'] if 'uploader' in rip_data else 'Northing'
        await v_url.edit(f"`Загружаю видосик:`\
        \n**{rip_data['title']}**\
        \nby *{u}*")
        await v_url.client.send_file(
            v_url.to_id,
            f"{rip_data['id']}.mp4",
            reply_to=reply.id if reply else None,
            supports_streaming=True,
            caption=rip_data['title'],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Загружаю...",
                         f"{rip_data['title']}.mp4")))
        os.remove(f"{rip_data['id']}.mp4")
        await v_url.delete()






CMD_HELP.update({'yt': '.yt <text>\
        \nUsage: выполняет поиск на YouTube.'})

CMD_HELP.update({
    'rip':
    '.rip audio <url> or rip video <url>\
        \nUsage: скачивайте видео и песни с YouTube (и [многие другие сайты](https://ytdl-org.github.io/youtube-dl/supportedsites.html)).'
})
