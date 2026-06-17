from db_for_udacha_v3 import *


bot = Bot("BOT TOKEN HERE")
dp = Dispatcher()
router = Router()

# Обертка для безопасного редактирования сообщений
async def safe_edit_text(message, text, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Игнорируем ошибку, если сообщение не изменилось
            pass
        else:
            # Пробрасываем другие ошибки
            raise

REQUEST_TIMEOUT = 5
NO_DATA = "нет данных"


def back_to_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
    ])


def clean_text(value):
    return " ".join(value.replace("\u2060", "").split())


def node_text(node, default=NO_DATA):
    if node is None:
        return default
    text = clean_text(node.get_text(" ", strip=True))
    return text or default


def fetch_soup(url):
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return None
    return BeautifulSoup(response.text, "html.parser")


def first_text(soup, selectors, default=NO_DATA):
    if soup is None:
        return default
    for selector in selectors:
        text = node_text(soup.select_one(selector), default="")
        if text:
            return text
    return default


def add_celsius_if_needed(value):
    if value != NO_DATA and "°" not in value:
        return f"{value} °C"
    return value


def build_weather_text():
    foreca = fetch_soup("https://www.foreca.com/100470378/Vyra-Leningradskaya-Oblast'-Russia")
    ru_meteo_hour = fetch_soup("https://ru-meteo.ru/vyra/hour")
    ru_meteo = fetch_soup("https://ru-meteo.ru/vyra")
    prognoz = fetch_soup("https://prognoz3.ru/россия/ленинградская-область/погода-в-деревне-выра")
    foreca_hourly = fetch_soup("https://www.foreca.com/ru/100470378/Vyra-Leningradskaya-Oblast'-Russia/hourly")

    temp = first_text(foreca, ["span.value.temp.temp_c"], default="")
    if not temp:
        temp = first_text(prognoz, [".temperature"])
    temp = add_celsius_if_needed(temp)

    conditions_next_hour = first_text(ru_meteo_hour, ["td.dsr"])
    water_temp = first_text(ru_meteo, ["span.n_tmp"])
    humidity = first_text(prognoz, ["span.humidity"])
    wind = first_text(prognoz, ["span.wind"])
    precip = first_text(foreca_hourly, ["span.value.rain.rain_mm"], default="")
    if not precip:
        precip = first_text(prognoz, ["span.precipitation"])

    return f'''☁️ Температура воздуха сейчас составляет: {temp}

🌤️ Погодные условия на следующий час: {conditions_next_hour}

💨 {wind}

💧 {humidity}

🌧️ Ожидаемое количество осадков в ближайшее время: {precip}

🌊 Температура воды составляет приблизительно: {water_temp} (+-3°) '''
    
# склонение времени
def decline_time(hours, minutes):
    hours = int(hours)
    minutes = int(minutes)
    def decline(num, forms):
        if 11 <= num % 100 <= 14:
            return forms[2]
        if num % 10 == 1:
            return forms[0]
        if 2 <= num % 10 <= 4:
            return forms[1]
        return forms[2]
    h = f"{hours} {decline(hours, ['час', 'часа', 'часов'])}"
    m = f"{minutes} {decline(minutes, ['минута', 'минуты', 'минут'])}"
    if hours > 0 and minutes > 0:
        return f"{h} и {m}"
    elif hours > 0:
        return h
    else:
        return m


def get_next_bus(current_time, schedule):
    k = 0
    start_time = datetime.strptime(schedule[k], '%H:%M').strftime('%H:%M')
    while current_time >= start_time and k != len(schedule) - 1:
        k += 1
        start_time = datetime.strptime(schedule[k], '%H:%M').strftime('%H:%M')
    if start_time < current_time:
        k = 0
    difference = str(datetime.strptime(schedule[k], '%H:%M') - datetime.strptime(current_time, '%H:%M'))
    return schedule[k], difference[0], difference[2:4]

# Создаем клавиатуры для автобусов
bus_main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="В Батово", callback_data="to_batovo"),
        InlineKeyboardButton(text="Из Батово", callback_data="from_batovo")
    ],
    [
        InlineKeyboardButton(text="В Сиверский", callback_data="to_siversky"),
        InlineKeyboardButton(text="Из Сиверской", callback_data="from_siversky")
    ],
    [InlineKeyboardButton(text="📅 Расписания", callback_data="schedules")],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

schedules_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="В Батово", callback_data="schedule_to_batovo"),
        InlineKeyboardButton(text="Из Батово", callback_data="schedule_from_batovo")
    ],
    [
        InlineKeyboardButton(text="В Сиверский", callback_data="schedule_to_siversky"),
        InlineKeyboardButton(text="Из Сиверской", callback_data="schedule_from_siversky")
    ],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]
])

@router.message(Command("start"))
async def start_message(message: Message):
    full_name = f'{message.from_user.first_name} {message.from_user.last_name}' if message.from_user.last_name else message.from_user.first_name
    await message.answer(f'👋 Приветствую, {full_name}!\n\nДобро пожаловать в бота для расписаний и погоды!\n\nВыберите раздел для получения информации:', reply_markup=help_kb)

help_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚌 Автобусы", callback_data="help_bus")],
    [InlineKeyboardButton(text="🚆 Электрички", callback_data="help_trains")],
    [InlineKeyboardButton(text="☁️ Погода", callback_data="help_weather")]
])

@router.message(Command("help"))
async def help(message: Message):
    await message.answer('''Этот бот помогает с расписаниями автобусов, электричек и информацией о погоде.\n\n- Для автобусов: Напишите \"автобус\" (или похожие слова) и выберите направление.\n- Для электричек: Используйте команду /trains и выберите маршрут.\n- Для погоды: Напишите \"погода\".\n\nНажмите на кнопки в меню или введите команды для быстрого доступа!''')

@router.callback_query(F.data == "help_bus")
async def help_bus(call: CallbackQuery):
    await safe_edit_text(call.message, "🚌 Выберите направление для нужного Вам автобуса:", reply_markup=bus_main_kb)

@router.callback_query(F.data == "help_trains")
async def help_trains(call: CallbackQuery):
    await safe_edit_text(call.message, "🚆 Выберите нужное Вам направление электрички:", reply_markup=v_siv_v_gor)

@router.callback_query(F.data == "help_weather")
async def help_weather(call: CallbackQuery):
    await safe_edit_text(call.message, "⏳ Обработка вашего запроса. Пожалуйста, подождите...")
    await safe_edit_text(call.message, build_weather_text(), reply_markup=back_to_start_keyboard())

@router.message(Command("trains"))
async def trains(message: Message):
    await message.answer('Выберите нужное вам направление ниже:', reply_markup=v_siv_v_gor)

# Список вариантов слова "автобус"
bus_keywords = [
    # Основные формы
    'автобус', 'автобусы', 'автобуса', 'автобусов', 'автобусе', 'автобусах', 
    # Уменьшительные формы
    'бусик', 'бусики', 'бусика', 'бусиков', 'бусике', 'бусиках',
    'бус', 'бусы', 'буса', 'бусов', 'бусе', 'бусах',
    'басик', 'басики', 'басика', 'басиков', 'басике', 'басиках',
    'автик', 'автики', 'автика', 'автиков', 'автике', 'автиках',
    # Прилагательные
    'автобусный', 'автобусная', 'автобусное', 'автобусные',
    # Синонимы
    'маршрутка', 'маршрутки', 'маршрутку', 'маршруток', 'маршрутке', 'маршрутках',
    'маршрут', 'маршруты', 'маршрута', 'маршрутов', 'маршруте', 'маршрутах',
    # Сокращения и опечатки
    'автобс', 'автобусс', 'афтобус', 'афтобусы', 'автобусик', 'автобусики'
]

@router.message(F.text)
async def send_text(message: Message):
    if message.text.lower() in bus_keywords:
        await message.answer("Выберите направление для нужного Вам автобуса:", reply_markup=bus_main_kb)
    ## ------------ПОГОДА-----------------------------------------------------------------------------------------------------------
    elif message.text.lower() == "погода":
        await message.answer("Обработка вашего запроса. Пожалуйста, подождите")
        await message.answer(build_weather_text())
        await message.delete()

    # ------------ПАСХАЛКИ-----------------------------------------------------------------------------------------------------------
    elif message.text.lower() == "иди нахуй" or message.text.lower() == "пошел нахуй":
        await message.answer('''
Kто там меня нахуй послал? 
Kому бан въебать?''')

    elif message.text.lower() == "этот бот просто имба" or message.text.lower() == "бот просто имба" or message.text.lower() == "бот имба" or message.text.lower() == "имба бот":
        await message.answer(f"Спасибо, {message.from_user.first_name}!")

    elif message.text.lower() == "этот бот просто хуйня" or message.text.lower() == "бот просто хуйня" or message.text.lower() == "бот хуйня" or message.text.lower() == "хуйня бот":
        await message.answer(f"Пошел нахуй, {message.from_user.first_name}!")
        await message.delete()

# Оптимизированная функция для получения следующего автобуса
async def get_next_bus_info(call: CallbackQuery, weekday_schedule, weekend_schedule, debug_name):
    current_time = datetime.now()
    current_day = current_time.strftime('%A')
    current_time = current_time.strftime('%H:%M')
    
    # Выбираем расписание в зависимости от дня недели
    schedule = weekend_schedule if current_day in ["Saturday", "Sunday"] else weekday_schedule
    
    # Получаем информацию о следующем автобусе
    next_time, hours, minutes = get_next_bus(current_time, schedule)
    
    # Формируем ответ
    await safe_edit_text(
        call.message,
        f'🚌 Следующий автобус будет в: {next_time}\n⏰ Он приедет через {decline_time(hours, minutes)}\n\ndebug_info: {debug_name}', 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],[InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]])
    )

# Обработчики для автобусов
@router.callback_query(F.data == "to_batovo")
async def to_batovo(call: CallbackQuery):
    await get_next_bus_info(call, mass_tuda_budni, mass_tuda_vihod, "mass_tuda_budni" if datetime.now().strftime('%A') not in ["Saturday", "Sunday"] else "mass_tuda_vihod")

@router.callback_query(F.data == "from_batovo")
async def from_batovo(call: CallbackQuery):
    await get_next_bus_info(call, mass_obratno_budni, mass_obratno_vihod, "mass_obratno_budni" if datetime.now().strftime('%A') not in ["Saturday", "Sunday"] else "mass_obratno_vihod")

@router.callback_query(F.data == "to_siversky")
async def to_siversky(call: CallbackQuery):
    await get_next_bus_info(call, siversky_tuda_budni, siversky_tuda_vihod, "siversky_tuda_budni" if datetime.now().strftime('%A') not in ["Saturday", "Sunday"] else "siversky_tuda_vihod")

@router.callback_query(F.data == "from_siversky")
async def from_siversky(call: CallbackQuery):
    await get_next_bus_info(call, siversky_obratno_budni, siversky_obratno_vihod, "siversky_obratno_budni" if datetime.now().strftime('%A') not in ["Saturday", "Sunday"] else "siversky_obratno_vihod")

# Общая функция для отображения расписаний
async def show_schedule(call: CallbackQuery, weekend_schedule, weekday_schedule, special_note=None):
    text = f'''
📅 Расписание на выходные:\n{', '.join(weekend_schedule)}\nРасписание на будни:\n{', '.join(weekday_schedule)}'''
    
    if special_note:
        text += f'''
{special_note}'''
        
    await safe_edit_text(
        call.message,
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📅  Назад к расписаниям", callback_data="schedules")],[InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_start")]])
    )

# Обработчики для расписаний
@router.callback_query(F.data == "schedules")
async def show_schedules(call: CallbackQuery):
    await safe_edit_text(call.message, "🚌 Выберите расписание для нужного Вам автобуса:", reply_markup=schedules_kb)

@router.callback_query(F.data == "schedule_to_batovo")
async def schedule_to_batovo(call: CallbackQuery):
    await show_schedule(call, mass_tuda_vihod, mass_tuda_budni)

@router.callback_query(F.data == "schedule_from_batovo")
async def schedule_from_batovo(call: CallbackQuery):
    await show_schedule(call, mass_obratno_vihod, mass_obratno_budni, "Расписание на субботу и воскресенье:\n5:45")

@router.callback_query(F.data == "schedule_to_siversky")
async def schedule_to_siversky(call: CallbackQuery):
    await show_schedule(call, siversky_tuda_vihod, siversky_tuda_budni, "Расписание на сб и вс:\n5:55")

@router.callback_query(F.data == "schedule_from_siversky")
async def schedule_from_siversky(call: CallbackQuery):
    await show_schedule(call, siversky_obratno_vihod, siversky_obratno_budni, "Расписание на сб и вс:\n5:15")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(call: CallbackQuery):
    await safe_edit_text(call.message, "🚌 Выберите направление для нужного Вам автобуса:", reply_markup=bus_main_kb)

@router.callback_query(F.data == "back_to_start")
async def back_to_start(call: CallbackQuery):
    full_name = f'{call.from_user.first_name} {call.from_user.last_name}' if call.from_user.last_name else call.from_user.first_name
    text = f'👋 Приветствую, {full_name}!\n\nДобро пожаловать в бота для расписаний и погоды!\n\nВыберите раздел для получения информации:'
    await safe_edit_text(call.message, text, reply_markup=help_kb)

#------------ЭЛЕКТРИЧКИ-----------------------------------------------------------------------------------------------------------
def format_train_answer(start_time, route, arrival, price, link):
    return f'''⏰ Время отправления: {start_time}
🚉 Маршрут поезда: {route}
🕒 Время прибытия: {arrival}
💰 Цена на поезд: {price}


🔗 Ссылка на расписание:
{link}
'''


def no_train_answer(link):
    return f'''⚠️ Не удалось найти ближайшую электричку в расписании.

Возможно, на сегодня больше нет рейсов или сайт расписания изменил разметку.

🔗 Ссылка на расписание:
{link}
'''


async def get_train_answer(link):
    try:
        response = requests.get(link, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return f'''⚠️ Не удалось загрузить расписание электричек.

Попробуйте открыть расписание по ссылке:
{link}
'''
    return await parsing(response=response, link=link)


async def send_train_schedule(call, link):
    answer = await get_train_answer(link)
    await safe_edit_text(call.message, answer, reply_markup=back_to_start_keyboard())


@router.callback_query(F.data.in_(['V_Siversky', 'V_Gorod']))
async def callback(call: CallbackQuery):
    if call.data == "V_Siversky":
        await safe_edit_text(call.message, "🚆 Выберите вашу начальную станцию:", reply_markup=vibor_iz_gor)
    elif call.data == 'V_Gorod':
        await safe_edit_text(call.message, "🚆 Вы едете из Гатчины, или из Сиверской?", reply_markup=iz_siv_iz_gor)

@router.callback_query(F.data.in_(['IZ_Gatchiny', "IZ_Siversky"]))
async def iz_gat_iz_siv(call: CallbackQuery):
    if call.data == "IZ_Gatchiny":
        await safe_edit_text(call.message, "🚆 Выберите вашу конечную станцию:", reply_markup=vibor_iz_gat)
    elif call.data == "IZ_Siversky":
        await safe_edit_text(call.message, "🚆 **Выберите вашу конечную станцию:**", reply_markup=vibor_iz_siv)

@router.callback_query(F.data.in_(['iz_gatchiny_v_balt', "iz_gatchiny_v_Len", 'iz_gatchiny_v_Aero', 'iz_gatchiny_v_Pushkin']))
async def iz_gat_v_gor(call: CallbackQuery):
    if call.data == 'iz_gatchiny_v_balt':
        await send_train_schedule(call, mass_iz_gatchina[0])
    elif call.data == "iz_gatchiny_v_Len":
        await send_train_schedule(call, mass_iz_gatchina[1])
    elif call.data == "iz_gatchiny_v_Aero":
        await send_train_schedule(call, mass_iz_gatchina[2])
    elif call.data == "iz_gatchiny_v_Pushkin":
        await send_train_schedule(call, mass_iz_gatchina[3])

@router.callback_query(F.data.in_(['iz_siversky_v_balt', 'iz_siversky_v_Len', 'iz_siversky_v_Aero', 'iz_siversky_v_Pushkin', 'iz_siversky_v_gatchinu']))
async def iz_siv_v_gor(call: CallbackQuery):
    if call.data == 'iz_siversky_v_balt':
        await send_train_schedule(call, mass_iz_siv[0])
    elif call.data == "iz_siversky_v_Len":
        await send_train_schedule(call, mass_iz_siv[1])
    elif call.data == "iz_siversky_v_Aero":
        await send_train_schedule(call, mass_iz_siv[2])
    elif call.data == "iz_siversky_v_Pushkin":
        await send_train_schedule(call, mass_iz_siv[3])
    elif call.data == "iz_siversky_v_gatchinu":
        await send_train_schedule(call, mass_iz_siv[4])

@router.callback_query(F.data.in_(['iz_balt_v_siv', 'iz_Len_v_siv', 'iz_Aero_v_siv', 'iz_Pushkin_v_siv', 'iz_Gatchina_v_siv']))
async def v_siv(call: CallbackQuery):
    if call.data == 'iz_balt_v_siv':
        await send_train_schedule(call, mass_v_siv[0])
    elif call.data == 'iz_Len_v_siv':
        await send_train_schedule(call, mass_v_siv[1])
    elif call.data == 'iz_Aero_v_siv':
        await send_train_schedule(call, mass_v_siv[2])
    elif call.data == 'iz_Pushkin_v_siv':
        await send_train_schedule(call, mass_v_siv[3])
    elif call.data == 'iz_Gatchina_v_siv':
        await send_train_schedule(call, mass_v_siv[4])

async def parsing(response, link):
    bs = BeautifulSoup(response.text, "html.parser")
    current_time = datetime.now().strftime('%H:%M')

    offer_cards = bs.select('[data-ti="offer-card"]')
    for card in offer_cards:
        start_time = node_text(card.select_one('[data-ti="departure-time"]'), default="")
        if not start_time or start_time <= current_time:
            continue

        route = node_text(card.select_one('[data-ti="offer-info"] a[href*="view.php"]'))
        arrival = node_text(card.select_one('[data-ti="arrival-time"]'))
        price = node_text(card.select_one('[data-ti="price"]'))
        return format_train_answer(start_time, route, arrival, price, link)

    train_start_time = [clean_text(item.get_text(" ", strip=True)) for item in bs.find_all('a', class_='g-link desktop__depTimeLink__1NA_N')]
    train_spawn_point = [clean_text(item.get_text(" ", strip=True)) for item in bs.find_all('td', class_='t-txt-s desktop__cell__2cdVW desktop__route__37GXG')]
    arrival_time = [clean_text(item.get_text(" ", strip=True)) for item in bs.find_all('a', class_='g-link desktop__arrTimeLink__2TJxM')]
    train_cost = [clean_text(item.get_text(" ", strip=True)) for item in bs.find_all('td', class_='t-txt-s desktop__cell__2cdVW desktop__price__31Jsd')]

    for start_time, route, arrival, price in zip(train_start_time, train_spawn_point, arrival_time, train_cost):
        if start_time > current_time:
            return format_train_answer(start_time, route, arrival, price, link)

    return no_train_answer(link)

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    # Исправление ошибки TelegramConflictError
    await dp.start_polling(
        bot, 
        skip_updates=True, 
        allowed_updates=['message', 'callback_query', 'my_chat_member', 'chat_member'],
        polling_timeout=10
    )

if __name__ == "__main__":
    asyncio.run(main())
