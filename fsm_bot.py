from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

storage = MemoryStorage()

user_dict: dict[int, dict[str, str | int, bool]] = {} #база данных пользователей

#Для каждого пользователя будет создаваться свой экземпляр класса FSMFillForm
class FSMFillForm(StatesGroup):
    #перечисляем возможные состояния бота
    fill_name = State() #состояние ожидания ввода имени
    fill_age = State()
    fill_gender = State()
    upload_photo = State()
    fill_education = State()
    fill_wish_news = State()
    
#Методы у FSMContext
#set_state get_state set_data get_data update_data clear

#вполучение state из мидлварей
#state: FSMContext = data.get('state')

@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text='Этот бот демонстрирует работу FSM\n\n'
                              'Чтобы перейти к заполнению анкеты - отправьте команду /fillform')
    
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Отменять нечего. Вы вне машины состояний.')

@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_in_state(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из машины состояний.' \
                              'Чтобы снова перейти к заполнению анкеты введите /fillform')
    await state.clear()
    
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите своё имя')
    await state.set_state(FSMFillForm.fill_name) #устанавливаем состояния ожидания ввода имени

@dp.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите ваш возраст')
    await state.set_state(FSMFillForm.fill_age)

@dp.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя. Введите имя.\n' \
        'Если хотите отмениить введение анкеты, то отправьте команду /cancel'
    )


@dp.message(StateFilter(FSMFillForm.fill_age), lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    male_button = InlineKeyboardButton(text='Мужской', callback_data='male')
    female_button = InlineKeyboardButton(text='Женский', callback_data='female')

    keyboard: list[list[InlineKeyboardButton]] = [[male_button, female_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text='Укажите ваш пол',
                         reply_markup=markup)
    await state.set_state(FSMFillForm.fill_gender)

@dp.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на Возраст. Введите число от 4 до 120.\n' \
        'Если хотите отмениить введение анкеты, то отправьте команду /cancel'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_gender), 
            F.data.in_(['male', 'female']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)

    await callback.message.delete() #удаляем сообщение с кнопками
    await callback.message.answer(text='Спасибо! А теперь загрузите своё фото')
    await state.set_state(FSMFillForm.upload_photo)


@dp.message(StateFilter(FSMFillForm.fill_gender))
async def warning_not_gender(message: Message):
    await message.answer(
        text='Пожалуйста, пользуйтесь кнопками при выборе пола.\n' \
        'Если хотите отмениить введение анкеты, то отправьте команду /cancel'
    )

@dp.message(StateFilter(FSMFillForm.upload_photo), F.photo[-1].as_('largest_photo')) #as_ - сохранение переменной из фильтров во внутрь хэндлера
async def process_photo_sent(message: Message, state: FSMContext, largest_photo: PhotoSize):
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )
    secondary_btn = InlineKeyboardButton(
        text='Среднее',
        callback_data='secondary'
    )
    higher_btn = InlineKeyboardButton(
        text='Высшее',
        callback_data='higher'
    )
    no_btn = InlineKeyboardButton(
        text='Нет',
        callback_data='no_edu'
    )
    keyboard: list[list[InlineKeyboardButton]] = [[secondary_btn, higher_btn], [no_btn]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(
        text='Спасибо!\n\nУкажите ваше образование',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.fill_education)

@dp.message(StateFilter(FSMFillForm.upload_photo))
async def warning_not_gender(message: Message):
    await message.answer(
        text='Пожалуйста, на этом шаге отправьте фото.\n' \
        'Если хотите отмениить введение анкеты, то отправьте команду /cancel'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_education),
            F.data.in_(['secondary', 'higher', 'no_edu']))
async def process_edu_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(education=callback.data)

    yes_news_btn = InlineKeyboardButton(
        text='Да',
        callback_data='yes_news'
    )
    no_news_btn = InlineKeyboardButton(
        text='Нет',
        callback_data='no_news'
    )
    keyboard: list[list[InlineKeyboardButton]] = [[yes_news_btn, no_news_btn]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_text(
        text='Спасибо!\n\nОстался последний шаг.\n'
              'Хотели бы вы получать новости',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.fill_wish_news)

@dp.message(StateFilter(FSMFillForm.fill_education))
async def warning_not_gender(message: Message):
    await message.answer(
        text='Пожалуйста, на этом шаге отправьте ответ с помощью кнопок.\n' \
        'Если хотите отмениить введение анкеты, то отправьте команду /cancel'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_wish_news),
            F.data.in_(['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(wish_news=callback.data == 'yes_news')
    user_dict[callback.from_user.id] = await state.get_data()
    await state.clear()
    await callback.message.edit_text(
        text='Спасибо! Ваши данные сохранены\n\nВы вышли из машины состояний'
    )
    await callback.message.answer(
        text='Чтобы посмотреть данные вашей анкеты - отправьте команду /showdata'
    )

@dp.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_not_wish_news(message: Message):
    await message.answer(
        text='Пожалуйста, на этом шаге отправьте ответ с помощью кнопок.\n' \
        'Если хотите отмениить введение анкеты, то отправьте команду /cancel'
    )

@dp.message(Command(commands='showdata'), StateFilter(default_state))
async def proccess_showdata_command(message: Message):
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Имя: {user_dict[message.from_user.id]["name"]}\n'
                    f'Возраст: {user_dict[message.from_user.id]["age"]}\n'
                    f'Пол: {user_dict[message.from_user.id]["gender"]}\n'
                    f'Образование: {user_dict[message.from_user.id]["education"]}\n'
                    f'Получать новости: {user_dict[message.from_user.id]["wish_news"]}\n'
        )
    else:
        await message.answer(
            text='Вы ещё не заполнили анкету. Чтобы начать - отправьте команду /fillform'
        )

@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Я ничего не понимаю :(')


if __name__ == '__main__':
    dp.run_polling(bot)