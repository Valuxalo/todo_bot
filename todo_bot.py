import pandas as pd
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config
from set_menu import set_main_menu
from lexicon import LEXICON, LEXICON_COMMANDS_RU

logger = logging.getLogger(__name__)


config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN, 
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()



def delete_data(PATH_TODO_TABLE) -> None:
    df = pd.read_csv(PATH_TODO_TABLE)
    df = df.iloc[0:0]
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')

PATH_TODO_TABLE = "todo_data/todo_table.csv"
COUNTER = 1
delete_data(PATH_TODO_TABLE)

storage = MemoryStorage()
class FSMFillForm(StatesGroup):
    #перечисляем возможные состояния бота
    fill_add = State() #состояние ожидания ввода имени
    fill_done = State()

@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON["/start"])
    logger.info('/start')
    
@dp.message(Command(commands='add'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    try:
        text = message.text.split(' ', 1)[1]
        new_data = {'id': [COUNTER], 'задача': [text], 'статус': ["active"]}
        df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
        df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
        df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
        COUNTER += 1
        await message.answer(text=LEXICON['task_add'])
    except IndexError:
        await message.answer(text=LEXICON['task_not_add'])
        await state.set_state(FSMFillForm.fill_add)
        logger.info(await state.get_state())

@dp.message(StateFilter(FSMFillForm.fill_add), F.text)
async def process_name_sent(message: Message, state: FSMContext):
    logger.info(message.text)
    global COUNTER
    text = message.text
    new_data = {'id': [COUNTER], 'задача': [text], 'статус': ["active"]}
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
    df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
    COUNTER += 1
    await message.answer(text=LEXICON['task_add'])
    await state.clear()

@dp.message(Command(commands='all'), StateFilter(default_state))
async def process_all_command(message: Message):
    logger.info('/all')
    df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
    await message.answer(f"<pre>{df.to_markdown(index=False)}</pre>", parse_mode=ParseMode.HTML)

@dp.message(Command(commands='done'))
async def process_done_command(message: Message, state: FSMContext):
    logger.info(message.text)
    try:
        num = int(message.text.split(' ', 1)[1])
        if 1 <= num < COUNTER:
            df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
            df.at[num-1, 'статус'] = "done"
            df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
            await message.answer(text=LEXICON['task_done'])
        else:
            await message.answer(text=LEXICON['task_not_numb'])
    except IndexError:
        await message.answer(text=LEXICON['task_not_done'])
        await state.set_state(FSMFillForm.fill_done)

@dp.message(StateFilter(FSMFillForm.fill_done), F.text.isdigit)
async def process_name_sent(message: Message, state: FSMContext):
    logger.info(message.text)
    num = int(message.text)
    if 1 <= num < COUNTER:
        df = pd.read_csv(PATH_TODO_TABLE, encoding='utf-8')
        df.at[num-1, 'статус'] = "done"
        df.to_csv(PATH_TODO_TABLE, index=False, encoding='utf-8')
        await message.answer(text=LEXICON['task_done'])
        await state.clear()
    else:
        await message.answer(text=LEXICON['task_not_numb'])

@dp.message(Command(commands='clear'))
async def process_cancel_command(message: Message):
    logger.info('/clear')
    delete_data(PATH_TODO_TABLE)

    await message.answer(text=LEXICON['clear'])

@dp.message()
async def send_echo(message: Message):
    logger.info(F"Uknown text: {message.text}")
    await message.reply(text='Я ничего не понимаю :(')


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await set_main_menu(bot)

if __name__ == '__main__':
    logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
    '[%(asctime)s] - %(name)s -%(message)s')

    logger.info('Starting bot') #начало работы бота
    dp.startup.register(on_startup)
    dp.run_polling(bot)