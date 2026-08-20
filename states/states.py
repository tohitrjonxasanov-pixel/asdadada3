from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_search_title = State()
    waiting_for_search_code = State()

class AdminAnimeAdd(StatesGroup):
    title = State()
    poster = State()
    genre = State()
    year = State()
    total_episodes = State()
    description = State()
    confirm = State()

class AdminAnimeEdit(StatesGroup):
    waiting_for_anime_code = State()
    waiting_for_field = State()
    waiting_for_new_value = State()

class AdminEpisodeAdd(StatesGroup):
    waiting_for_code = State()
    waiting_for_number = State()
    waiting_for_video = State()

class AdminEpisodeEdit(StatesGroup):
    waiting_for_code = State()
    waiting_for_select_ep = State()
    waiting_for_action = State()
    waiting_for_new_video = State()
    waiting_for_new_number = State()

class AdminEpisodeDelete(StatesGroup):
    waiting_for_code = State()
    waiting_for_number = State()

class AdminChannelAdd(StatesGroup):
    waiting_for_username = State()

class AdminUserSearch(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_message = State()

class AdminAddState(StatesGroup):
    waiting_for_admin_id = State()

class AdminSettingsEdit(StatesGroup):
    waiting_for_start_text = State()
    waiting_for_sub_text = State()

