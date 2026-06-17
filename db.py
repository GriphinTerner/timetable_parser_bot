from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import asyncio
from datetime import datetime
import requests
from bs4 import BeautifulSoup

#МАССИВЫ ДЛЯ АВТОБУСОВ

#СВЕРХУ МАССИВ НА ВЫХОДНЫЕ СНИЗУ НА БУДНИ при движении в батово
mass_tuda_vihod = ["4:15", "5:25", "6:26", "6:45", "8:05", "8:58", "9:50", "11:05", "12:00", "12:48", "13:15", "15:20", "15:46", "16:55", "17:55", "19:28", "19:30", "20:59", "21:05", "22:00", "23:55",]
mass_tuda_budni = ["4:15", "5:25", "6:26", "6:40", "6:45", "7:40", "8:05", "8:45", "8:58", "9:50", "10:20", "11:5", "12:00", "12:48", "13:15", "14:45", "15:20", "15:46", "15:55", "16:55", "17:30", "17:55", "18:50", "19:28", "19:30", "20:59", "21:05", "22:00", "23:55"]

#СВЕРХУ МАССИВ НА ВЫХОДНЫЕ СНИЗУ НА БУДНИ при движении назад из батово
mass_obratno_vihod = ["00:00", "6:35", "7:10", "8:25", "9:25", "10:10", "11:20", "12:25", "13:20", "15:40", "16:27", "17:15", "18:10", "19:40", "19:45", "21:00", "21:20", "22:20"]
mass_obratno_budni = ["00:00", "4:30", "5:20", "6:35", "7:00", "7:10", "8:0", "8:25", "9:00", "9:25", "10:10", "10:35", "11:20", "12:25", "13:20", "14:50", "15:40", "16:20", "16:27", "17:15", "17:50", "18:10", "19:00", "19:40", "19:45", "21:00", "21:20", "22:20"]

#СВЕРХУ МАССИВ НА ВЫХОДНЫЕ СНИЗУ НА БУДНИ при движении в сиверский
siversky_tuda_vihod = ["0:10", "6:35", "7:20", "8:12", "8:35", "9:25", "10:20", "11:30", "12:35", "13:40", "15:50", "17:25", "18:20", "19:55", "21:30", "22:30"]
siversky_tuda_budni= ["0:10", "4:40", "5:30", "6:35", "7:10", "7:20", "8:10", "8:12", "8:35", "9:10", "9:25", "10:20", "10:45", "11:30", "12:35", "13:40", "15:0", "15:50", "16:30", "17:25", "18:00", "18:20", "19:10", "19:55", "21:30", "22:30"]

#СВЕРХУ МАССИВ НА ВЫХОДНЫЕ СНИЗУ НА БУДНИ при движении из сиверской
siversky_obratno_vihod= ["6:40", "7:55", "9:40", "10:55", "11:50", "13:5", "14:25", "15:10", "16:45", "17:45", "19:20", "20:55", "21:50", "23:45"]
siversky_obratno_budni = ["4:05", "4:55", "6:30", "6:40", "7:30", "7:55", "8:35", "9:40", "10:10", "10:55", "11:50", "13:05", "14:25", "14:25", "15:10", "15:45", "16:45", "17:20", "17:45", "18:40", "19:20", "20:55", "21:50", "23:45"]

# МАССИВЫ ДЛЯ ЭЛЕКТРИЧЕК
balt_siv = "https://www.tutu.ru/spb/rasp.php?st1=181&st2=4481"
len_siv = 'https://www.tutu.ru/spb/rasp.php?st1=481&st2=4481'
aero_siv = 'https://www.tutu.ru/spb/rasp.php?st1=5281&st2=4481'
pushkin_siv = 'https://www.tutu.ru/spb/rasp.php?st1=5381&st2=4481'
gatchina_siv = 'https://www.tutu.ru/spb/rasp.php?st1=4081&st2=4481'

siv_balt = 'https://www.tutu.ru/spb/rasp.php?st1=4481&st2=181'
siv_len = 'https://www.tutu.ru/spb/rasp.php?st1=4481&st2=481'
siv_aero = 'https://www.tutu.ru/spb/rasp.php?st1=4481&st2=5281'
siv_pushkin = 'https://www.tutu.ru/spb/rasp.php?st1=4481&st2=5381'
siv_gatchina = 'https://www.tutu.ru/spb/rasp.php?st1=4481&st2=4081'

gatchina_balt = 'https://www.tutu.ru/spb/rasp.php?st1=4081&st2=181'
gatchina_len = 'https://www.tutu.ru/spb/rasp.php?st1=4081&st2=481'
gatchina_aero = 'https://www.tutu.ru/spb/rasp.php?st1=4081&st2=5281'
gatchina_pushkin = 'https://www.tutu.ru/spb/rasp.php?st1=4081&st2=5381'

mass_v_siv = [balt_siv, len_siv, aero_siv, pushkin_siv, gatchina_siv]
mass_iz_siv = [siv_balt, siv_len, siv_aero, siv_pushkin, siv_gatchina]
mass_iz_gatchina = [gatchina_balt, gatchina_len, gatchina_aero, gatchina_pushkin]

# КЛАВИАТУРЫ ДЛЯ ЭЛЕКТРИЧЕК
v_siv_v_gor = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В Сиверский", callback_data="V_Siversky")],
    [InlineKeyboardButton(text="В Город", callback_data='V_Gorod')],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

iz_siv_iz_gor = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Из Сиверской", callback_data="IZ_Siversky")],
    [InlineKeyboardButton(text="Из Гатчины", callback_data='IZ_Gatchiny')],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

vibor_iz_gat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Балтийский Вокзал", callback_data="iz_gatchiny_v_balt")],
    [InlineKeyboardButton(text="Ленинский Проспект", callback_data='iz_gatchiny_v_Len')],
    [InlineKeyboardButton(text="Аэропорт", callback_data="iz_gatchiny_v_Aero")],
    [InlineKeyboardButton(text="Александровская (Пушкин)", callback_data='iz_gatchiny_v_Pushkin')],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

vibor_iz_siv = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Балтийский Вокзал", callback_data="iz_siversky_v_balt")],
    [InlineKeyboardButton(text="Ленинский Проспект", callback_data='iz_siversky_v_Len')],
    [InlineKeyboardButton(text="Аэропорт", callback_data="iz_siversky_v_Aero")],
    [InlineKeyboardButton(text="Александровская (Пушкин)", callback_data='iz_siversky_v_Pushkin')],
    [InlineKeyboardButton(text="Гатчина - Варшавская", callback_data="iz_siversky_v_gatchinu")],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

vibor_iz_gor = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Балтийский Вокзал", callback_data="iz_balt_v_siv")],
    [InlineKeyboardButton(text="Ленинский Проспект", callback_data='iz_Len_v_siv')],
    [InlineKeyboardButton(text="Аэропорт", callback_data="iz_Aero_v_siv")],
    [InlineKeyboardButton(text="Александровская (Пушкин)", callback_data='iz_Pushkin_v_siv')],
    [InlineKeyboardButton(text="Гатчина - Варшавская", callback_data="iz_Gatchina_v_siv")],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

#ДЛЯ ПАРСИНГА
headers = requests.utils.default_headers()
headers.update({'User-Agent': 'GriphinTerner'})
