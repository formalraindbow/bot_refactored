from telebot.handler_backends import State, StatesGroup

class TicketPurchaseStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_university = State()
    waiting_for_faculty = State()
    waiting_for_info_source = State()
    waiting_for_confirmation = State()
    
