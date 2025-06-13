import json #загрузка списка слов
import random #рандомные задания с эмоджи
import pandas as pd #работа с корпусом слов из словарика
from telegram import Update  #сообщение от пользователя
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes #нужные функции для бота

emoji_tasks = json.load(open("data/emoji_tasks.json", "r", encoding="utf-8"))
words_df = pd.read_csv("data/words_ru_en_zh.csv")

user_states = {} #сохранить определенное задание

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = {"mode": "menu"} #находится в главном меню
    await update.message.reply_text(
        "Здравствуйте! Я NichosiStudies — помощник учителей и детей-билингвов 🇷🇺🇬🇧🇨🇳\n"
        "Напишите /emoji — угадайте слово по эмодзи\n"
        "или /translate — получите перевод на трёх языках!"
    )

async def emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = random.choice(emoji_tasks)
    user_states[update.effective_user.id] = {
        "mode": "emoji",
        "answer_ru": task["answer_ru"].lower(),
        "answer_en": task["answer_en"].lower(),
        "answer_zh": task["answer_zh"]
    }
    await update.message.reply_text(f"Угадай, что это: {task['emoji']}")

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    row = words_df.sample().iloc[0]
    user_states[update.effective_user.id] = {
        "mode": "translate",
        "answer_ru": row["word_ru"].lower(),
        "answer_en": row["word_en"].lower(),
        "answer_zh": row["word_zh"]
    }
    await update.message.reply_text(f"Как будет «{row['word_ru']}» на английском и китайском?")

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if user_id not in user_states:
        await update.message.reply_text("Напишите /start, чтобы начать.")
        return

    state = user_states[user_id]

    if state["mode"] == "emoji":
        if text in [state["answer_ru"], state["answer_en"], state["answer_zh"]]:
            await update.message.reply_text(
                f"Отлично! Ответ:\n"
                f"🇷🇺 {state['answer_ru']}\n"
                f"🇬🇧 {state['answer_en']}\n"
                f"🇨🇳 {state['answer_zh']}"
            )
        else:
            await update.message.reply_text("Не совсем, попробуй ещё раз или напиши /emoji для нового задания.")

    elif state["mode"] == "translate":
        await update.message.reply_text(
            f"Правильный перевод:\n"
            f"🇬🇧 {state['answer_en']}\n"
            f"🇨🇳 {state['answer_zh']}"
        )
    else:
        await update.message.reply_text("Напишите /emoji или /translate, чтобы начать.")

if __name__ == "__main__":
    app = ApplicationBuilder().token("7895954616:AAHstYswXpY1mTnVwHaLQlC8SLXRJUO2KPc").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("emoji", emoji))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    print("Бот запущен...")
    app.run_polling()