import os, json, requests
from .. import loader, utils

# https://t.me/clown_228

def register(cb):
	cb(VirusMod())

class VirusMod(loader.Module):
	strings = {'name': 'VirusTotal @clown_clown'}
	def __init__(self):
		self.name = self.strings['name']
		self._me = None
		self._ratelimit = []

	async def scancmd(self, message):
		""".scan [Reply на файл]"""
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("<b>Reply на файл</b>")
			return
		else:
			for i in os.listdir():
				if "file" in i:
					os.system(f"rm -rf {i}")
			await message.edit("<b>Загружаем...</b>")
			await reply.download_media('file')
			for i in os.listdir():
				if "file" in i:
					fil = i
			if not fil:
				await message.edit("<b>Это не файл")
				return
			await message.edit("<b>Чекаю...</b>") 
			if fil not in ["file.jpg", "file.png", "file.ico", "file.mp3", "file.mp4", "file.gif", "file.txt"]: 
				token = "d0c9094b17cb32063499738588fa39a500b829b5ef21944a0f621898773d8900"
				params = dict(apikey = token)
				with open(fil, 'rb') as file:
					files = dict(file=(fil, file))
					response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan', files=files, params=params)
				os.system(f"rm -rf {fil}")
				try:
					if response.status_code == 200:
						false = []
						true = []
						result=response.json()
						res = (json.dumps(result, sort_keys=False, indent=4)).split()[10].split('"')[1]
						params = dict(apikey = token, resource=res)
						response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
						if response.status_code == 200:
							result = response.json()
							for key in result['scans']:
								if result['scans'][key]['detected']:
									false.append(f'⛔️ {key}')
								else:
									true.append(f'✅ {key}')
						await message.edit(f"🧬 Найдено: {len(false)} / {len(result['scans'])}\n" + '\n'.join(false)+ "\n" + '\n'.join(true) + "\n\n" + f'''⚜️<a href="t.me/clown_228">Немножечко рекламы</a>''')
				except:
					await message.edit("<b>Не получилось чекнуть файл</b>")
			else:
				await message.edit("<b>Я не могу чекнуть данный формат файла, он не поддерживается.</b>")
				os.system(f"rm -rf {fil}")
