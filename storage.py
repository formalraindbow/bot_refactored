import json
import os
from config import USERS_DATA_FILE, VALID_PAYMENTS_FILE
from models import User
import logger 
def load_users():
    try:
        with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {int(user_id): User.from_dict(user_data) for user_id, user_data in data.items()}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка при загрузке пользователей: {e}")
        return {}

def save_users(users):
    with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
        data = {str(user_id): user.to_dict() for user_id, user in users.items()}
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_valid_list():
    try:
        with open(VALID_PAYMENTS_FILE, 'r', encoding='UTF-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_valid_list(valid_list):
    try:
        with open(VALID_PAYMENTS_FILE, 'w', encoding='UTF-8') as f:
            json.dump(valid_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении {VALID_PAYMENTS_FILE}: {e}")
        