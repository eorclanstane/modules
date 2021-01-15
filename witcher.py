import logging
import pyowm
import math

from .. import loader, utils

from ..utils import escape_html as eh

logger = logging.getLogger(__name__)


def deg_to_text(deg):
    if deg is None:
        return None
    return ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW",
            "SW", "WSW", "W", "WNW", "NW", "NNW"][round(deg / 22.5) % 16]


def round_to_sf(n, digits):
    return round(n, digits - 1 - int(math.floor(math.log10(abs(n)))))


@loader.tds
class WeatherMod(loader.Module):
    """Проверяет погоду
       Получить ключ API нужно на https://openweathermap.org/appid"""
    strings = {"name": "Погода",
               "provide_api": "<b>Пожалуйста, предоставьте ключ API через режим конфигурации.</b>",
               "invalid_temp_units": "<b>Недопустимые единицы измерения температуры. Пожалуйста, перенастройте модуль.</b>",
               "doc_default_loc": "Идентификатор города OpenWeatherMap",
               "doc_api_key": "Ключ API на https://openweathermap.org/appid",
               "doc_temp_units": "Единица измерения температуры на английском языке",
               "result": "<b>Погода в {loc} - {w} с максимумом {high} и минимумом"
                         " {low}, в среднем {avg} с {humid} влажностью и ветром {ws}mph {wd}.</b>",
               "unknown": "unknown"}

    def __init__(self):
        self.config = loader.ModuleConfig("DEFAULT_LOCATION", None, lambda m: self.strings("doc_default_loc", m),
                                          "API_KEY", None, lambda m: self.strings("doc_api_key", m),
                                          "TEMP_UNITS", "celsius", lambda m: self.strings("doc_temp_units", m))
        self._owm = None

    def config_complete(self):
        if self.config["API_KEY"]:
            self._owm = pyowm.OWM(self.config["API_KEY"]).weather_manager()
        else:
            self._owm = None

    @loader.unrestricted
    @loader.ratelimit
    async def weathercmd(self, message):
        """.weather [локация]"""
        if self._owm is None:
            await utils.answer(message, self.strings("provide_api", message))
            return
        args = utils.get_args_raw(message)
        func = None
        if not args:
            func = self._owm.weather_at_id
            args = [self.config["DEFAULT_LOCATION"]]
        else:
            try:
                args = [int(args)]
                func = self._owm.weather_at_id
            except ValueError:
                coords = utils.get_args_split_by(message, ",")
                if len(coords) == 2:
                    try:
                        args = [int(coord.strip()) for coord in coords]
                        func = self._owm.weather_at_coords
                    except ValueError:
                        pass
        if func is None:
            func = self._owm.weather_at_place
            args = [args]
        logger.debug(func)
        logger.debug(args)
        o = await utils.run_sync(func, *args)
        logger.debug("Weather at %r is %r", args, o)
        try:
            w = o.weather
            temp = w.get_temperature(self.config["TEMP_UNITS"])
        except ValueError:
            await utils.answer(message, self.strings("invalid_temp_units", message))
            return
        ret = self.strings("result", message).format(loc=eh(o.get_location().get_name()),
                                                     w=eh(w.get_detailed_status().lower()),
                                                     high=eh(temp["temp_max"]), low=eh(temp["temp_min"]),
                                                     avg=eh(temp["temp"]), humid=eh(w.get_humidity()),
                                                     ws=eh(round_to_sf(w.get_wind("miles_hour")["speed"], 3)),
                                                     wd=eh(deg_to_text(w.get_wind().get("deg", None))
                                                           or self.strings("unknown", message)))
        await utils.answer(message, ret)