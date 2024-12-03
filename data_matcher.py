import json
import gspread
from google.oauth2.service_account import Credentials
import re
from fuzzywuzzy import fuzz
from logger import logger
from config import (
    JSON_FILE_PATH,
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME
)

class DataMatcher:
    def __init__(self, json_file_path, credentials_path, sheet_id, sheet_name):
        self.json_file_path = json_file_path
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.json_data = {}
        self.sheet_data = []

    def load_json(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            logger.info(f"JSON данные загружены из {self.json_file_path}.")
        except FileNotFoundError:
            logger.error(f"Файл JSON не найден: {self.json_file_path}.")
        except json.JSONDecodeError:
            logger.error(f"Ошибка декодирования JSON из файла: {self.json_file_path}.")

    def connect_to_google_sheets(self):
        expected_headers = ['№', 'Фамилия', 'Имя', 'Отчество', 'ВУЗ', 'Деньги', 'Билет', 'Способ', 'Дата']
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            client = gspread.authorize(creds)
            sheet = client.open_by_key(self.sheet_id).worksheet(self.sheet_name)
            self.sheet_data = sheet.get_all_records()
            logger.info(f"Данные из Google Sheets ({self.sheet_name}) успешно загружены.")
        except FileNotFoundError:
            logger.error(f"Файл учетных данных не найден: {self.credentials_path}.")
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Google Sheet с ID {self.sheet_id} не найден.")
        except Exception as e:
            logger.error(f"Ошибка при подключении к Google Sheets: {e}")

    @staticmethod
    def normalize_name(name):
        return re.sub(r'\s+', ' ', name.replace("ё", "е").replace("Ё", "Е")).strip().lower()

    def prepare_json_data(self):
        normalized_data = {}
        for username, details in self.json_data.items():
            if len(details) < 4:
                logger.warning(f"Недостаточно данных для пользователя {username}.")
                continue
            user_id, last_name, first_name, middle_name = details[:4]
            full_name = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            normalized_full_name = self.normalize_name(full_name)
            normalized_data[normalized_full_name] = user_id
        logger.debug("JSON данные нормализованы.")
        return normalized_data

    def prepare_sheet_data(self):
        normalized_data = {}
        for row in self.sheet_data:
            try:
                full_name = f"{row['Фамилия']} {row['Имя']} {row['Отчество']}"
                normalized_full_name = self.normalize_name(full_name)
                normalized_data[normalized_full_name] = row  # Сохраняем всю строку для дальнейшего анализа
            except KeyError as e:
                logger.error(f"Отсутствует ожидаемый заголовок в Google Sheets: {e}")
        logger.debug("Данные из Google Sheets нормализованы.")
        return normalized_data

    def fuzzy_match_names(self, name, sheet_normalized):
        matches = []
        for sheet_name in sheet_normalized:
            similarity = fuzz.ratio(name, sheet_name)
            if 90 < similarity < 100:  # Порог схожести, можно настроить
                matches.append((sheet_name, similarity))
        return matches

    def match_data(self):
        json_normalized = self.prepare_json_data()
        sheet_normalized = self.prepare_sheet_data()

        missing_in_sheet = [name for name in json_normalized if name not in sheet_normalized]
        missing_in_json = [name for name in sheet_normalized if name not in json_normalized]

        # Хранение имен с латиницей или спец. символами
        latin_or_special_names = set()

        # Сверка данных и поиск нечетких совпадений
        fuzzy_matches_output = []
        for sheet_name in sheet_normalized:
            if sheet_name not in json_normalized:
                # Проверка на наличие латиницы или спец. символов
                if re.search(r'[a-zA-Z!$%&/()=?@#^*;:<>~`"{},$begin:math:display$$end:math:display$\\]', sheet_name):
                    latin_or_special_names.add(sheet_name)

                # Выполнение нечеткого сравнения
                fuzzy_matches = self.fuzzy_match_names(sheet_name, json_normalized)
                for match_name, similarity in fuzzy_matches:
                    fuzzy_matches_output.append(
                        f"{sheet_name} (из таблицы) похоже на {match_name} (из JSON) с схожестью {similarity}%"
                    )

        # Формирование результата для отправки
        result = ""
        if fuzzy_matches_output:
            result += "<b>Нечеткие совпадения:</b>\n"
            result += "\n".join(fuzzy_matches_output) + "\n\n"

        if missing_in_sheet:
            result += "<b>Отсутствуют в Google Таблице:</b>\n"
            result += ", ".join(missing_in_sheet) + "\n\n"

        if missing_in_json:
            result += "<b>Отсутствуют в JSON:</b>\n"
            result += ", ".join(missing_in_json) + "\n\n"

        if latin_or_special_names:
            result += "<b>На латинице или со спец. символами:</b>\n"
            result += ", ".join(latin_or_special_names) + "\n\n"

        if not result:
            result = "Все данные совпадают идеально!"

        return result

    def run(self):
        self.load_json()
        self.connect_to_google_sheets()
        result = self.match_data()
        return result

# Пример использования:
# matcher = DataMatcher(JSON_FILE_PATH, GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID, GOOGLE_SHEET_NAME)
# result = matcher.run()
# print(result)