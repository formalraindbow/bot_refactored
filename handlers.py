import telebot
from telebot import types
from datetime import datetime
import pytz

from logger import logger
from data_matcher import DataMatcher

from config import (
    API_TOKEN,
    TEXTS,
    VALID_PAYMENTS_FILE,
    MENUS,
    TARGET_USER_ID,
    JSON_FILE_PATH,
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME
)
from models import User
from storage import load_users, save_users, load_valid_list, save_valid_list

from states import TicketPurchaseStates

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Загрузка пользователей из файла
users = load_users()
logger.info("Бот успешно инициализирован и пользователи загружены.")

def create_keyboard(menu_name):
    """
    Создаёт клавиатуру на основе конфигурации меню.

    :param menu_name: Название меню из конфигурации MENUS
    :return: Объект InlineKeyboardMarkup
    """
    keyboard = types.InlineKeyboardMarkup()
    buttons = MENUS.get(menu_name, {}).get('buttons', [])
    for button in buttons:
        btn = types.InlineKeyboardButton(
            text=button['text'],
            callback_data=button['callback_data']
        )
        keyboard.add(btn)
    logger.debug(f"Клавиатура для меню '{menu_name}' создана.")
    return keyboard


def send_menu(user_id, menu_name, user_data=None, custom_keyboard=None):
    """
    Отправляет меню пользователю с указанным именем меню.

    :param user_id: Идентификатор пользователя
    :param menu_name: Название меню из конфигурации MENUS
    :param user_data: Дополнительные данные для форматирования текста
    :param custom_keyboard: Пользовательская клавиатура (если есть)
    """
    menu = MENUS.get(menu_name)
    if not menu:
        logger.error(f"Меню '{menu_name}' не найдено в конфигурации.")
        return

    # Создаём клавиатуру
    keyboard = create_keyboard(menu_name)

    # Если передана пользовательская клавиатура, используем её вместо стандартной
    if custom_keyboard:
        keyboard = custom_keyboard
        logger.debug(f"Использована пользовательская клавиатура для меню '{menu_name}'.")

    # Определяем тип медиа-файлов
    media_photos = []
    media_documents = []
    for media_file in menu['media']:
        if media_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            media_photos.append(media_file)
        elif media_file.lower().endswith(('.pdf', '.docx', '.txt')):
            media_documents.append(media_file)
        else:
            logger.warning(f"Неизвестный тип файла: {media_file}")

    # Отправляем фотографии, если они есть
    if media_photos:
        media_group = []
        for photo in media_photos:
            try:
                with open(photo, 'rb') as f:
                    media_group.append(types.InputMediaPhoto(f.read()))
                logger.debug(f"Фотография '{photo}' добавлена в группу медиа.")
            except FileNotFoundError:
                logger.error(f"Файл {photo} не найден.")
        if media_group:
            try:
                bot.send_media_group(user_id, media=media_group)
                logger.info(f"Группа фотографий отправлена пользователю {user_id}.")
            except Exception as e:
                logger.error(f"Ошибка при отправке медиа-группы пользователю {user_id}: {e}")

    # Отправляем документы, если они есть
    for doc in media_documents:
        try:
            with open(doc, 'rb') as f:
                bot.send_document(user_id, f)
            logger.info(f"Документ '{doc}' отправлен пользователю {user_id}.")
        except FileNotFoundError:
            logger.error(f"Документ {doc} не найден.")
        except Exception as e:
            logger.error(f"Ошибка при отправке документа '{doc}' пользователю {user_id}: {e}")

    # Форматируем текст, если предоставлены данные
    text = menu['text'].format(**user_data) if user_data else menu['text']

    # Отправляем сообщение с клавиатурой
    try:
        bot.send_message(user_id, text, reply_markup=keyboard, parse_mode='HTML')
        logger.debug(f"Отправлено меню '{menu_name}' пользователю {user_id}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения меню '{menu_name}' пользователю {user_id}: {e}")


def send_result(user_id):
    """
    Отправляет результат автосверки пользователю.

    :param user_id: Идентификатор пользователя
    :return: Результат сверки данных
    """
    matcher = DataMatcher(
        json_file_path=str(JSON_FILE_PATH),
        credentials_path=str(GOOGLE_CREDENTIALS_PATH),
        sheet_id=GOOGLE_SHEET_ID,
        sheet_name=GOOGLE_SHEET_NAME
    )
    result = matcher.run()
    if not result:
        result = "Нет данных для сверки."
    logger.debug(f"Результат сверки для пользователя {user_id}: {result}")
    return result


def handle_send_result(call):
    """
    Обработчик кнопки 'Провести сверку'.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    logger.debug(f"Пользователь {user_id} инициировал сверку данных.")

    # Выполняем сверку данных
    result = send_result(user_id)

    # Отправляем результат пользователю
    try:
        bot.send_message(
            user_id,
            f'<b>Схожести:</b>\n{result}',
            parse_mode='HTML'
        )
        logger.info(f"Результат сверки отправлен пользователю {user_id}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке результата сверки пользователю {user_id}: {e}")

    # Закрываем callback
    bot.answer_callback_query(call.id)
    logger.debug(f"Callback для сверки данных пользователя {user_id} закрыт.")


def buy_ticket(call):
    """
    Обработчик покупки билета.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    user = users.get(user_id)
    logger.debug(f"Пользователь {user_id} инициировал покупку билета.")

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при попытке купить билет.")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте заново /start")
        return

    # Отправляем инструкции по оплате
    try:
        bot.send_message(user_id, TEXTS['payment_instructions'], parse_mode="Markdown")
        logger.info(f"Отправлены инструкции по оплате пользователю {user_id}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке инструкций по оплате пользователю {user_id}: {e}")

    # Переходим к состоянию ожидания ввода ФИО
    try:
        bot.set_state(user_id, TicketPurchaseStates.waiting_for_name, call.message.chat.id)
        logger.debug(f"Пользователь {user_id} переведен в состояние ожидания имени.")
    except Exception as e:
        logger.error(f"Ошибка при установке состояния ожидания имени для пользователя {user_id}: {e}")


@bot.message_handler(state=TicketPurchaseStates.waiting_for_university)
def process_university(message):
    """
    Обработчик ввода ВУЗа пользователя.

    :param message: Объект Message
    """
    user_id = message.from_user.id
    user = users.get(user_id)
    university_input = message.text.strip()
    logger.debug(f"Пользователь {user_id} отправил название ВУЗа: '{university_input}'.")

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при обработке ВУза.")
        bot.send_message(user_id, "Произошла ошибка. Попробуйте заново /start")
        bot.delete_state(user_id)
        return

    if not university_input:
        logger.info(f"Пользователь {user_id} отправил пустое название ВУЗа.")
        bot.send_message(user_id, "Пожалуйста, введите корректное название ВУЗа.")
        return

    user.university = university_input
    save_users(users)
    logger.info(f"Пользователь {user_id} установил ВУЗ: {university_input}.")

    # Переходим к следующему состоянию
    try:
        bot.set_state(user_id, TicketPurchaseStates.waiting_for_faculty)
        logger.debug(f"Пользователь {user_id} переведен в состояние ожидания факультета.")
    except Exception as e:
        logger.error(f"Ошибка при установке состояния ожидания факультета для пользователя {user_id}: {e}")

    # Отправляем меню выбора факультета
    send_menu(user_id, 'faculty_menu')
    logger.debug(f"Отправлена клавиатура факультетов пользователю {user_id}.")


def handle_faculty_selection(call):
    """
    Обработчик выбора факультета.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    user = users.get(user_id)
    logger.debug(f"Пользователь {user_id} выбрал факультет: {call.data}.")

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при выборе факультета.")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте заново /start")
        bot.delete_state(user_id)
        return

    # Извлекаем ключ факультета из callback_data
    try:
        faculty_key = call.data.split('faculty_')[1]
    except IndexError:
        logger.error(f"Некорректный формат callback_data: {call.data}")
        bot.answer_callback_query(call.id, "Некорректный выбор факультета.")
        return

    # Определяем название факультета
    faculties = {
        'social_studies': 'Социальные науки',
        'computer_studies': 'Компьютерные науки',
        'human_studies': 'Гуманитарные науки',
        'natural_studies': 'Естественные науки',
        'physical_studies': 'Физические науки',
        'another_studies': 'Другое/не учусь в вузе'
    }

    faculty = faculties.get(faculty_key)
    if faculty:
        user.faculty = faculty
        save_users(users)
        logger.info(f"Пользователь {user_id} установил факультет: {faculty}.")

        # Переходим к следующему состоянию
        try:
            bot.set_state(user_id, TicketPurchaseStates.waiting_for_info_source)
            logger.debug(f"Пользователь {user_id} переведен в состояние ожидания источника информации.")
        except Exception as e:
            logger.error(f"Ошибка при установке состояния ожидания источника информации для пользователя {user_id}: {e}")

        # Отправляем меню выбора источника информации
        send_menu(user_id, 'info_source_menu')
    else:
        logger.error(f"Неизвестный факультет выбран пользователем {user_id}: {faculty_key}")
        bot.answer_callback_query(call.id, "Неизвестный факультет.")


def handle_event_info(call):
    """
    Обработчик информации о мероприятии.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    send_menu(user_id, 'event_info_menu')
    logger.debug(f"Отправлено меню информации о мероприятии пользователю {user_id}.")


def handle_event_venue(call):
    """
    Обработчик места проведения мероприятия.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    send_menu(user_id, 'menu_osninfo')
    logger.debug(f"Отправлено меню места проведения пользователю {user_id}.")


def handle_event_schedule(call):
    """
    Обработчик расписания мероприятия.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    send_menu(user_id, 'menu_pravila')
    logger.debug(f"Отправлено меню расписания мероприятия пользователю {user_id}.")


def handle_event_map(call):
    """
    Обработчик карты местности мероприятия.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    send_menu(user_id, 'menu_bar')
    logger.debug(f"Отправлено меню карты местности пользователю {user_id}.")


def handle_loft_menu(call):
    """
    Обработчик плана лофта.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    send_menu(user_id, 'menu_loft')
    logger.debug(f"Отправлено меню плана лофта пользователю {user_id}.")


def handle_main_menu(call):
    """
    Обработчик возврата в главное меню.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    user = users.get(user_id)

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при возврате в главное меню.")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте заново /start")
        return

    if user.is_registered:
        menu_name = 'main_menu_registered'
        user_data = {'first_name': user.first_name}
    else:
        menu_name = 'main_menu_new'
        user_data = {'first_name': user.first_name}

    # Отправляем главное меню
    send_menu(user_id, menu_name, user_data=user_data)
    logger.info(f"Пользователь {user_id} вернулся в главное меню.")


def handle_info_source_selection(call):
    """
    Обработчик выбора источника информации.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    user = users.get(user_id)
    logger.debug(f"Пользователь {user_id} выбрал источник информации: {call.data}.")

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при выборе источника информации.")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте заново /start")
        bot.delete_state(user_id)
        return

    # Извлекаем ключ источника информации из callback_data
    try:
        source_key = call.data.split('info_source_')[1]
    except IndexError:
        logger.error(f"Некорректный формат callback_data: {call.data}")
        bot.answer_callback_query(call.id, "Некорректный выбор источника информации.")
        return

    # Определяем название источника информации
    sources = {
        'friends': 'От друзей',
        'odnogroup': 'От одногруппников/однокурсников',
        'social': 'Из соцсетей',
        'posvat': 'Пришел/а с посвята',
        'another': 'Другое'
    }

    source = sources.get(source_key)
    if source:
        user.info_source = source
        save_users(users)
        logger.info(f"Пользователь {user_id} установил источник информации: {source}.")

        # Переходим к следующему состоянию
        try:
            bot.set_state(user_id, TicketPurchaseStates.waiting_for_confirmation)
            logger.debug(f"Пользователь {user_id} переведен в состояние ожидания подтверждения.")
        except Exception as e:
            logger.error(f"Ошибка при установке состояния ожидания подтверждения для пользователя {user_id}: {e}")

        # Отправляем подтверждение данных
        user_data = {
            'name': user.name,
            'university': user.university,
            'faculty': user.faculty,
            'info_source': user.info_source
        }
        send_menu(user_id, 'confirmation_menu', user_data)
    else:
        logger.error(f"Неизвестный источник информации выбран пользователем {user_id}: {source_key}")
        bot.answer_callback_query(call.id, "Неизвестный источник информации.")


def handle_confirmation(call):
    """
    Обработчик подтверждения данных.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    user = users.get(user_id)
    logger.debug(f"Пользователь {user_id} отправил подтверждение: {call.data}.")

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при подтверждении данных.")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте заново /start")
        bot.delete_state(user_id)
        return

    if call.data == 'confirm_yes':
        user.is_registered = True
        save_users(users)
        logger.info(f"Пользователь {user_id} подтвердил данные и зарегистрировался.")

        bot.answer_callback_query(call.id)
        
        # Отправляем меню успешной регистрации
        send_menu(user_id, 'main_menu_registered')
        logger.debug(f"Отправлено подтверждение регистрации пользователю {user_id}.")

        # Удаляем состояние пользователя
        try:
            bot.delete_state(user_id)
            logger.debug(f"Состояние пользователя {user_id} удалено после подтверждения регистрации.")
        except Exception as e:
            logger.error(f"Ошибка при удалении состояния пользователя {user_id}: {e}")

    elif call.data == 'confirm_no':
        logger.info(f"Пользователь {user_id} отказался от подтверждения данных. Начинаем заново.")
        bot.answer_callback_query(call.id)
        try:
            bot.send_message(user_id, TEXTS['enter_name_text'])
            bot.set_state(user_id, TicketPurchaseStates.waiting_for_name)
            logger.debug(f"Пользователь {user_id} переведен в состояние ожидания имени для повторной регистрации.")
        except Exception as e:
            logger.error(f"Ошибка при перенаправлении пользователя {user_id} на повторную регистрацию: {e}")
    else:
        logger.error(f"Неизвестная команда подтверждения от пользователя {user_id}: {call.data}")
        bot.answer_callback_query(call.id, "Неизвестная команда.")


@bot.message_handler(state=TicketPurchaseStates.waiting_for_name)
def process_name(message):
    """
    Обработчик ввода имени пользователя.

    :param message: Объект Message
    """
    user_id = message.from_user.id
    user = users.get(user_id)
    name_input = message.text.strip()
    logger.debug(f"Пользователь {user_id} начал обработку имени.")

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при обработке имени.")
        bot.send_message(user_id, "Произошла ошибка. Попробуйте заново /start")
        bot.delete_state(user_id)
        return

    if not name_input:
        logger.info(f"Пользователь {user_id} отправил пустое имя.")
        bot.send_message(user_id, "Пожалуйста, введите корректное ФИО.")
        return

    user.name = name_input
    save_users(users)
    logger.info(f"Пользователь {user_id} установил ФИО: {name_input}.")

    # Переходим к следующему состоянию
    try:
        bot.set_state(user_id, TicketPurchaseStates.waiting_for_university)
        logger.debug(f"Пользователь {user_id} переведен в состояние ожидания ВУЗа.")
    except Exception as e:
        logger.error(f"Ошибка при установке состояния ожидания ВУЗа для пользователя {user_id}: {e}")

    # Отправляем сообщение для ввода ВУЗа
    try:
        bot.send_message(
            user_id,
            "Напишите, из какого вы ВУЗа.\n\nЕсли вы не учитесь в ВУЗе, то напишите «Нигде»."
        )
        logger.debug(f"Отправлено сообщение для ввода ВУЗа пользователю {user_id}.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения для ввода ВУза пользователю {user_id}: {e}")


def handle_buy_ticket(call):
    """
    Обработчик покупки билета через callback.

    :param call: Объект CallbackQuery
    """
    buy_ticket(call)


def handle_change_data(call):
    """
    Обработчик изменения данных пользователя.

    :param call: Объект CallbackQuery
    """
    user_id = call.from_user.id
    user = users.get(user_id)

    if not user:
        logger.warning(f"Пользователь {user_id} не найден при попытке изменить данные.")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте заново /start")
        return

    # Сбрасываем данные пользователя
    user.name = None
    user.university = None
    user.faculty = None
    user.is_registered = False
    save_users(users)
    logger.info(f"Пользователь {user_id} сбросил свои данные для обновления.")

    # Отправляем уведомление и переходим к состоянию ввода имени
    try:
        bot.answer_callback_query(call.id)
        bot.send_message(user_id, "Давайте обновим ваши данные. Пожалуйста, напишите свое ФИО.")
        bot.set_state(user_id, TicketPurchaseStates.waiting_for_name, call.message.chat.id)
        logger.debug(f"Пользователь {user_id} переведен в состояние ожидания имени для обновления данных.")
    except Exception as e:
        logger.error(f"Ошибка при перенаправлении пользователя {user_id} на обновление данных: {e}")


def check_oplata(message):
    """
    Обработчик подтверждения оплаты.

    :param message: Объект Message
    """
    user_id = str(message.from_user.id)
    valid_list = load_valid_list()
    logger.debug(f"Загружен список валидных оплат: {valid_list}.")

    if user_id in valid_list:
        valid_list[user_id] += 1
        save_valid_list(valid_list)
        logger.info(f"Пользователь {user_id} подтвердил оплату. Обновленный счетчик: {valid_list[user_id]}.")

        try:
            # Отправляем меню успешной оплаты
            send_menu(message.from_user.id, 'payment_success_menu')
            logger.debug(f"Отправлено меню успешной оплаты пользователю {user_id}.")
        except Exception as e:
            logger.error(f"Ошибка при отправке меню успешной оплаты пользователю {user_id}: {e}")
    else:
        logger.warning(f"Пользователь {user_id} не найден в списке валидных оплат.")
        try:
            # Отправляем меню ошибки оплаты
            send_menu(message.from_user.id, 'payment_error_menu')
            logger.debug(f"Отправлено меню ошибки оплаты пользователю {user_id}.")
        except Exception as e:
            logger.error(f"Ошибка при отправке меню ошибки оплаты пользователю {user_id}: {e}")


# Словарь соответствия callback_data обработчикам
callback_handlers = {
    'buy_ticket': handle_buy_ticket,
    'change_data': handle_change_data,
    'confirm_yes': handle_confirmation,
    'confirm_no': handle_confirmation,
    'menu_osninfo': handle_event_venue,
    'menu_pravila': handle_event_schedule,
    'menu_bar': handle_event_map,
    'menu_loft': handle_loft_menu,
    'menu_main': handle_main_menu,
    'send__result': handle_send_result,
    # Обработчики факультетов
    'faculty_social_studies': handle_faculty_selection,
    'faculty_computer_studies': handle_faculty_selection,
    'faculty_human_studies': handle_faculty_selection,
    'faculty_natural_studies': handle_faculty_selection,
    'faculty_physical_studies': handle_faculty_selection,
    'faculty_another_studies': handle_faculty_selection,
    # Обработчики источников информации
    'info_source_friends': handle_info_source_selection,
    'info_source_odnogroup': handle_info_source_selection,
    'info_source_social': handle_info_source_selection,
    'info_source_posvat': handle_info_source_selection,
    'info_source_another': handle_info_source_selection,
    'event_info': handle_event_info,
    # Добавьте другие обработчики при необходимости
    'check_payment': check_oplata
}


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
    Обработчик всех callback-запросов.

    :param call: Объект CallbackQuery
    """
    handler = callback_handlers.get(call.data)
    if handler:
        logger.debug(f"Вызван обработчик для callback_data: '{call.data}' от пользователя {call.from_user.id}.")
        try:
            handler(call)
        except Exception as e:
            logger.error(f"Ошибка в обработчике '{call.data}' для пользователя {call.from_user.id}: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка при обработке запроса.")
    else:
        logger.warning(f"Неизвестная команда callback_data: '{call.data}' от пользователя {call.from_user.id}.")
        bot.answer_callback_query(call.id, "Неизвестная команда.")


@bot.message_handler(commands=['start'])
def start(message):
    """
    Обработчик команды /start.

    :param message: Объект Message
    """
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    first_name = message.from_user.first_name
    logger.info(f"Пользователь {user_id} запустил команду /start.")

    # Проверяем, есть ли пользователь в базе
    user = users.get(user_id)

    if not user:
        # Создаем нового пользователя
        user = User(user_id, username, first_name)
        # Устанавливаем дату регистрации
        tz_moscow = pytz.timezone('Europe/Moscow')
        user.registration_date = datetime.now(tz_moscow).isoformat()
        users[user_id] = user
        save_users(users)
        logger.info(f"Создан новый пользователь {user_id} с именем {first_name}.")

    # Выбираем соответствующий текст приветствия и меню
    if user.is_registered:
        menu_name = 'main_menu_registered'
        user_data = {'first_name': user.first_name}
    else:
        menu_name = 'main_menu_new'
        user_data = {'first_name': user.first_name}

    keyboard = create_keyboard(menu_name)

    # Если пользователь в TARGET_USER_ID, добавляем кнопку "Провести сверку"
    if user_id in TARGET_USER_ID:
        try:
            send_button = types.InlineKeyboardButton(
                text='Провести сверку',
                callback_data='send__result'
            )
            keyboard.add(send_button)
            logger.debug(f"Добавлена кнопка 'Провести сверку' для пользователя {user_id}.")
        except Exception as e:
            logger.error(f"Ошибка при добавлении кнопки 'Провести сверку' для пользователя {user_id}: {e}")

    # Отправляем главное меню
    send_menu(user_id, menu_name, user_data=user_data, custom_keyboard=keyboard)
    logger.info(f"Отправлено приветственное сообщение пользователю {user_id}.")