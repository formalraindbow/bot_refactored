from pathlib import Path

API_TOKEN = '7842066700:AAEnHVYoMAiBEmNuGNamsJunE_6_jacC2Dg'
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)
STORAGE_DIR = DATA_DIR / 'storage'
# Пути для DataMatcher
JSON_FILE_PATH = STORAGE_DIR / 'guests_ns2024.json'  # Перенесите guests_ns2024.json в storage
GOOGLE_CREDENTIALS_PATH = STORAGE_DIR / 'ns2024-683591222f43.json'
GOOGLE_SHEET_ID = '1gqk90fr4vkybdKPLmSf1gUEcUeMt4LXNQbTRpG8wOlo'
GOOGLE_SHEET_NAME = 'Продажи билетов'
TARGET_USER_ID = {438251622, 872471903, 5669158349, 102255626, 621562696}

VALID_PAYMENTS_FILE = DATA_DIR / 'guests_valid.json'

USERS_DATA_FILE = DATA_DIR / 'users.json'



TEXTS = {
    'welcome_registered': (
        "Проснись, {first_name}!\n\n"
        "Пора готовиться к самой незабываемой ночёвке года, которая пройдёт с 16 на 17 ноября. "
        "Собирай своих друзей, доставай пижаму и готовься веселиться всю ночь напролёт!\n\n"
        "Выбери информацию, которую желаешь узнать."
    ),
    'welcome_new': (
        "Проснись, {first_name}!\n\n"
        "Пора готовиться к самой незабываемой ночёвке года, которая пройдёт с 16 на 17 ноября. "
        "Собирай своих друзей, доставай пижаму и готовься веселиться всю ночь напролёт!\n\n"
        "Выбери информацию, которую желаешь узнать."
    ),
    'payment_instructions': """
    Ты можешь приобрести билет на Ночь Социолога по одному из двух тарифов:

    _Power Nap_: проход на мероприятие и напиток при соблюдении дресс-кода! Стоимость: *1200*₽

    _Insomnia_: проход на мероприятие, напиток при соблюдении дресс-кода и три коктейля на твой выбор! Стоимость: *1800*₽

    *ВАЖНО*: При покупке билета обязательно укажи *ФИО* и *свой ВУЗ* в сообщении к переводу.

    ТИНЬКОФФ:
    `2200 7009 8887 1918`

    СБЕР:
    `5469 9804 2458 6929`

    По номеру телефона:
    `+7 (903) 051-97-02`
    Евгений Андреевич А.

    *ПОСЛЕ СОВЕРШЕНИЯ ОПЛАТЫ*

    Пожалуйста, напиши свое *ФИО*

    _Пример: Иванов Иван Иванович_

    _Если ты начал/а процесс регистрации, пожалуйста, пройди его до конца. Если после введения ФИО бот не дает ответа — нажми заново /start_
        """,
    'payment_success': "Поздравляем, твоя путевка оформлена! Ждем тебя в нашем лагере 5-6 октября, следи за обновлениями в нашем [канале](https://t.me/socposvyat2024).",
    'payment_error': "Ой! Кажется, духи перехватили твою оплату. Пожалуйста, напиши @roman_khamrin.",
    'link_mero': 't.me/peachteamcommunity', 
    'event_map': ''
}


MENUS = {
    'main_menu_new': {
        'text': TEXTS['welcome_new'],
        'buttons': [
            {'text': 'Купить билет', 'callback_data': 'buy_ticket'},
            {'text': 'Подтверждение оплаты', 'callback_data': 'check_payment'},
            {'text': 'Информация о мероприятии', 'callback_data': 'event_info'}
        ],
        'media': [] 
    },
    'main_menu_registered': {
        'text': TEXTS['welcome_registered'],
        'buttons': [
            {'text': 'Изменить данные', 'callback_data': 'change_data'},
            {'text': 'Подтверждение оплаты', 'callback_data': 'check_payment'},
            {'text': 'Информация о мероприятии', 'callback_data': 'event_info'}
        ],
        'media': []  
    },
    'event_info_menu': {
        'text': "Информация о мероприятии:",
        'buttons': [
            {'text': 'Место проведения', 'callback_data': 'menu_osninfo'},
            {'text': 'Расписание', 'callback_data': 'menu_pravila'},
            {'text': 'Карта местности', 'callback_data': 'menu_bar'},
            {'text': 'Чек-лист', 'callback_data': 'menu_checklist'},
            {'text': 'ТГ сожителей', 'callback_data': 'menu_tg'},
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': []  
    },
    'menu_osninfo': {
        'text': "Место проведения мероприятия:",
        'buttons': [
            {'text': 'Расписание', 'callback_data': 'menu_pravila'},
            {'text': 'Карта местности', 'callback_data': 'menu_bar'},
            {'text': 'ТГ сожителей', 'callback_data': 'menu_tg'},
            {'text': 'Чек-лист', 'callback_data': 'menu_checklist'},
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': [
            str(STORAGE_DIR / '1.jpg'),
            str(STORAGE_DIR / '1.jpg'),
            str(STORAGE_DIR / '1.jpg'),
            str(STORAGE_DIR / '1.jpg'),
        ]
    },
    'menu_pravila': {
        'text': "Расписание мероприятия:",
        'buttons': [
            {'text': 'Место проведения', 'callback_data': 'menu_osninfo'},
            {'text': 'Карта местности', 'callback_data': 'menu_bar'},
            {'text': 'ТГ сожителей', 'callback_data': 'menu_tg'},
            {'text': 'Чек-лист', 'callback_data': 'menu_checklist'},
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': [
            str(STORAGE_DIR / 'timeline.png'),
        ]
    },
    'menu_loft': {
        'text': "План лофта:",
        'buttons': [
            {'text': 'Барная карта', 'callback_data': 'menu_bar'},
            {'text': 'Место проведения', 'callback_data': 'menu_osninfo'},
            {'text': 'ТГ сожителей', 'callback_data': 'menu_tg'},
            {'text': 'Чек-лист', 'callback_data': 'menu_checklist'},
            {'text': 'Расписание', 'callback_data': 'menu_pravila'},
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': [
            str(STORAGE_DIR / 'loft.jpg')
        ]
    },
    'menu_bar': {
        'text': "Карта местности:",
        'buttons': [
            {'text': 'Расписание', 'callback_data': 'menu_pravila'},
            {'text': 'Место проведения', 'callback_data': 'menu_osninfo'},
            {'text': 'ТГ сожителей', 'callback_data': 'menu_tg'},
            {'text': 'Чек-лист', 'callback_data': 'menu_checklist'},
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': [
            str(STORAGE_DIR / 'loft.jpg')
        ]
    },
    'confirmation_menu': {
        'text': "Пожалуйста, проверьте введенные данные:\n\nФИО: {name}\nВУЗ: {university}\nФакультет: {faculty}\nИсточник информации: {info_source}\n\nВсе верно?",
        'buttons': [
            {'text': 'Да', 'callback_data': 'confirm_yes'},
            {'text': 'Нет', 'callback_data': 'confirm_no'}
        ],
        'media': []
    },
    'info_source_menu': {
        'text': "Откуда вы узнали о мероприятии?",
        'buttons': [
            {'text': 'От друзей', 'callback_data': 'info_source_friends'},
            {'text': 'От одногруппников/однокурсников', 'callback_data': 'info_source_odnogroup'},
            {'text': 'Из соцсетей', 'callback_data': 'info_source_social'},
            {'text': 'Пришел/а с посвята', 'callback_data': 'info_source_posvat'},
            {'text': 'Другое', 'callback_data': 'info_source_another'}
        ],
        'media': []  
    },
    'main_menu_button': {
        'text': "Выйти в главное меню:",
        'buttons': [
            {'text': 'Выйти в главное меню', 'callback_data': 'menu_main'}
        ],
        'media': []
    },
    'payment_success_menu': {
        'text': TEXTS['payment_success'].format(link=TEXTS['link_mero']),
        'buttons': [
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': [] 
    },
    'payment_error_menu': {
        'text': TEXTS['payment_error'],
        'buttons': [
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': [] 
    },
    'faculty_menu': {
        'text': "Выберите ваш факультет:",
        'buttons': [
            {'text': 'Социальные науки', 'callback_data': 'faculty_social_studies'},
            {'text': 'Компьютерные науки', 'callback_data': 'faculty_computer_studies'},
            {'text': 'Гуманитарные науки', 'callback_data': 'faculty_human_studies'},
            {'text': 'Естественные науки', 'callback_data': 'faculty_natural_studies'},
            {'text': 'Физические науки', 'callback_data': 'faculty_physical_studies'},
            {'text': 'Другое/не учусь в вузе', 'callback_data': 'faculty_another_studies'},
            {'text': 'Главное меню', 'callback_data': 'menu_main'}
        ],
        'media': []  
    },
    # Добавьте другие меню по аналогии
}