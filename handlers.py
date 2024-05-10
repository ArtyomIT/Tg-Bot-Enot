from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import F
from aiogram import Dispatcher
from aiogram.filters.command import Command
from quiz_data import quiz_data
from database import get_quiz_index, update_quiz_index, get_user_score, update_user_score, get_all_scores

# Диспетчер
dp = Dispatcher()


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        text = f"{option}|{'right_answer' if option == right_answer else 'wrong_answer'}"
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=text
        )
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(lambda c: c.data.endswith('answer'))
async def process_callback(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_score = await get_user_score(callback.from_user.id)

    current_question_index = await get_quiz_index(callback.from_user.id)
    await callback.message.answer(f"Ваш ответ {callback.data.split('|')[0]} и это...")
    if callback.data.split('|')[-1] == 'right_answer':
        await callback.message.answer("Правильный ответ!")
        current_score += 1
        await update_user_score(callback.from_user.id, current_score)
    else:
        correct_option = quiz_data[current_question_index]['correct_option']
        await callback.message.answer(f"Неверно! Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {current_score}/10 правильных ответов.")


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    new_score = 0
    await update_user_score(user_id, new_score)
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


# Хэндлер на команду /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(f"Команды бота: \n/start - начать взаимодействие с ботом\n/help - открыть помощь \n/quiz - начать игру \n/stats - вывести статистику")


# Хэндлер на команду /stats
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    scores = await get_all_scores()
    response = "Статистика всех игроков:\n\n"
    mid = 0
    i = 1
    for user_id, score in scores:
        mid += score
        response += f"{i}. Пользователь {user_id}: {score} правильных ответов\n\n"
        i += 1
    response += f"Средний бал всех игроков: {mid/len(scores)}"
    await message.answer(response)
