LEXICON: dict[str, str] = {
    '/start': '<b>Привет!</b>\n\nЭто todo-бот, в котором '
              'ты можешь сохранить список задач, '
              'отметить их выполнение и потом очистить список, когда всё выполнится!\n\n'
              '<b>Список доступных команд:</b>\n\n'
              ' /all - список всех задач 📝\n'
              ' /add &quot;текст задачи&quot; - добавить задачу 📌\n'
              ' /done &quot;номер задачи&quot; - завершить задачу ✅\n'
              ' /clear - очистить список задач ⭕️\n',
    '/help': '',
    'task_add': '📌 задача добавлена',
    'task_not_add': 'Введите текст задачи',
    'task_not_numb': 'Такой задачи нет',
    'task_done': '✅ задача завершена',
    'task_not_done': 'Введите номер задачи',
    'clear': '⭕️ список задач очищен'
}

LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Начало работы с ботом',
    '/all': 'Список задач',
    '/add': 'Добавить задачу',
    '/done': 'Завершить задачу',
    '/clear': 'Очистить список задач'
}