import asyncio
import logging
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "9193723377:AAEqC63aWr23PmJUResLubAjavalheEP3kE"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("quiz_bot")

# ---------------------------------------------------------------------------
# Саволҳо: (матн, [4 ҷавоб], индекси ҷавоби дуруст)
# ---------------------------------------------------------------------------
QUESTIONS = [
    {
        "text": "🇹🇯 Пойтахти Тоҷикистон кадом шаҳр аст?",
        "options": ["Хуҷанд", "Кӯлоб", "Душанбе", "Бохтар"],
        "correct": 2,
    },
    {
        "text": "🏔 Баландтарин қуллаи Тоҷикистон кадом аст?",
        "options": [
            "Қуллаи Ибни Сино",
            "Қуллаи Исмоили Сомонӣ",
            "Қуллаи Корженевская",
            "Қуллаи Фанн",
        ],
        "correct": 1,
    },
    {
        "text": "📅 Тоҷикистон дар кадом сол истиқлолияти давлатиро эълон кард?",
        "options": ["1989", "1991", "1992", "1997"],
        "correct": 1,
    },
    {
        "text": "🐍 Забони барномасозии Python-ро кӣ эҷод кардааст?",
        "options": [
            "Линус Торвалдс",
            "Деннис Ритчи",
            "Гвидо ван Россум",
            "Бярне Страуструп",
        ],
        "correct": 2,
    },
    {
        "text": "💻 HTML маънои чӣ дорад?",
        "options": [
            "HyperText Markup Language",
            "High Transfer Machine Language",
            "Home Tool Markup Language",
            "HyperText Modern Logic",
        ],
        "correct": 0,
    },
    {
        "text": "📝 Дар Python шарҳро (comment) бо кадом аломат оғоз мекунанд?",
        "options": ["//", "#", "/* */", "--"],
        "correct": 1,
    },
    {
        "text": "🔴 Кадом сайёра бо номи «Сайёраи сурх» маъруф аст?",
        "options": ["Зӯҳра", "Муштарӣ", "Миррих", "Зуҳал"],
        "correct": 2,
    },
    {
        "text": "🌍 Дар рӯи Замин чандто уқёнус вуҷуд дорад?",
        "options": ["3", "4", "5", "7"],
        "correct": 2,
    },
    {
        "text": "➗ 12 × 12 ба чанд баробар аст?",
        "options": ["124", "122", "144", "164"],
        "correct": 2,
    },
    {
        "text": "🧮 Решаи квадратии адади 169 ба чанд баробар аст?",
        "options": ["11", "12", "13", "14"],
        "correct": 2,
    },
]

TOTAL = len(QUESTIONS)


@dataclass
class UserState:
    index: int = 0          # индекси саволи ҷорӣ
    score: int = 0          # шумораи ҷавобҳои дуруст
    answered: bool = False  # оё саволи ҷорӣ аллакай ҷавоб дода шудааст


# Ҳолати корбарон дар хотира: user_id -> UserState
users: dict[int, UserState] = {}

dp = Dispatcher()


def question_text(index: int) -> str:
    q = QUESTIONS[index]
    return f"<b>Савол {index + 1} аз {TOTAL}</b>\n\n{q['text']}"


def question_keyboard(index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for opt_idx, option in enumerate(QUESTIONS[index]["options"]):
        builder.button(text=option, callback_data=f"ans:{index}:{opt_idx}")
    builder.adjust(2)
    return builder.as_markup()


def play_again_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔄 Бозии нав", callback_data="restart")]]
    )


def result_message(score: int) -> str:
    if score == TOTAL:
        comment = "🏆 Аъло! Шумо ҳамаи саволҳоро дуруст ҷавоб додед!"
    elif score >= 7:
        comment = "👏 Хеле хуб! Натиҷаи олӣ."
    elif score >= 4:
        comment = "👍 Нағз! Боз як бор кӯшиш кунед."
    else:
        comment = "💪 Хавотир нашавед, бори дигар кӯшиш кунед!"
    return f"🏁 <b>Бозӣ тамом шуд!</b>\n\n📊 Натиҷаи шумо: <b>{score} аз {TOTAL}</b>\n\n{comment}"


async def start_quiz(bot: Bot, chat_id: int, user_id: int) -> None:
    users[user_id] = UserState()
    await bot.send_message(chat_id, question_text(0), reply_markup=question_keyboard(0))


@dp.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    user = message.from_user
    logger.info("/start from user %s", user.id)
    await message.answer(
        f"👋 Салом, <b>{user.full_name}</b>!\n\n"
        f"Хуш омадед ба бозии викторина. Дар ин ҷо {TOTAL} савол интизори шумост "
        "(Тоҷикистон, барномасозӣ, донишҳои умумӣ ва математика).\n\n"
        "Бозӣ оғоз мешавад! 🚀"
    )
    await start_quiz(bot, message.chat.id, user.id)


@dp.callback_query(F.data == "restart")
async def on_restart(callback: CallbackQuery, bot: Bot) -> None:
    logger.info("Restart from user %s", callback.from_user.id)
    await callback.answer()
    # Тугмаи «Бозии нав»-ро аз паёми натиҷа тоза мекунем, то дубора пахш нашавад
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await start_quiz(bot, callback.message.chat.id, callback.from_user.id)


@dp.callback_query(F.data.startswith("ans:"))
async def on_answer(callback: CallbackQuery, bot: Bot) -> None:
    user_id = callback.from_user.id
    state = users.get(user_id)

    if state is None:
        await callback.answer("Бозӣ ёфт нашуд. Лутфан /start-ро пахш кунед.", show_alert=True)
        return

    try:
        _, q_idx_str, opt_idx_str = callback.data.split(":")
        q_idx, opt_idx = int(q_idx_str), int(opt_idx_str)
    except ValueError:
        await callback.answer()
        return

    # Муҳофизат аз пахши дубора / ҷавоб ба саволи кӯҳна
    if q_idx != state.index or state.answered:
        await callback.answer("Шумо ба ин савол аллакай ҷавоб додаед!", show_alert=False)
        return

    state.answered = True
    question = QUESTIONS[q_idx]
    correct_idx = question["correct"]

    if opt_idx == correct_idx:
        state.score += 1
        verdict = "✅ Дуруст!"
    else:
        verdict = f"❌ Нодуруст! Ҷавоби дуруст: {question['options'][correct_idx]}"

    logger.info(
        "User %s answered q%d with option %d (%s)",
        user_id, q_idx + 1, opt_idx, "correct" if opt_idx == correct_idx else "wrong",
    )

    # Паёми саволро иваз мекунем ва тугмаҳоро мебарорем
    await callback.message.edit_text(
        f"{question_text(q_idx)}\n\n{verdict}",
        reply_markup=None,
    )
    await callback.answer()

    # Саволи навбатӣ ё натиҷаи ниҳоӣ
    state.index += 1
    state.answered = False
    chat_id = callback.message.chat.id

    if state.index < TOTAL:
        await bot.send_message(
            chat_id,
            question_text(state.index),
            reply_markup=question_keyboard(state.index),
        )
    else:
        await bot.send_message(
            chat_id,
            result_message(state.score),
            reply_markup=play_again_keyboard(),
        )
        logger.info("User %s finished with score %d/%d", user_id, state.score, TOTAL)


async def main() -> None:
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("Лутфан TOKEN-ро дар болои файл бо токени бот иваз кунед.")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("Бот оғоз шуд...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот қатъ карда шуд.")
