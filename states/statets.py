from aiogram.fsm.state import State, StatesGroup

class next_step(StatesGroup):
    admin =State()
    kino_id = State()
    name = State()
    des = State()
    url = State()
    delete_kino = State()
    waiting_for_ad_text = State()  
    waiting_for_photo = State()
    waiting_for_video = State()
    waiting_for_ad_type = State()
    waiting_for_text = State()

class start_step(StatesGroup):
    start_bot = State()

    
