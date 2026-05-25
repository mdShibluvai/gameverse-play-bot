import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8656599791:AAHXX6KhbEe64TELutCxs1OUJZjNvql5a64"
WEB_URL = "https://gameverse-play-bot.onrender.com"

GAMES = {
    "snake":  "🐍 Snake",
    "car":    "🏎️ Car Racing",
    "jump":   "🏀 Jump Ball",
    "chess":  "♟️ Chess",
    "ludo":   "🎲 Ludo",
}

def load_games_html():
    try:
        with open("games.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>games.html not found!</h1>"

GAMES_HTML = load_games_html()

async def game_page(request):
    return web.Response(text=GAMES_HTML, content_type="text/html", headers={
        "Content-Security-Policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://telegram.org; style-src 'unsafe-inline' 'self'; script-src 'unsafe-inline' 'unsafe-eval' https://telegram.org;"
    })

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for i, (key, name) in enumerate(GAMES.items()):
        btn = InlineKeyboardButton(name, web_app=WebAppInfo(url=f"{WEB_URL}/play?game={key}"))
        row.append(btn)
        if len(row) == 2 or i == len(GAMES) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton("🔄 মেনু রিফ্রেশ", callback_data="refresh")])
    await update.message.reply_text(
        "🎮 *GameVerse Play* 🎮\n\nখেলা বেছে নাও!\nপ্রতিটি খেলা তোমার ফোনেই চলবে 🔥",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "refresh":
        keyboard = []
        row = []
        for i, (key, name) in enumerate(GAMES.items()):
            btn = InlineKeyboardButton(name, web_app=WebAppInfo(url=f"{WEB_URL}/play?game={key}"))
            row.append(btn)
            if len(row) == 2 or i == len(GAMES) - 1:
                keyboard.append(row)
                row = []
        keyboard.append([InlineKeyboardButton("🔄 মেনু রিফ্রেশ", callback_data="refresh")])
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

async def main():
    web_app = web.Application()
    web_app.add_routes([web.get("/play", game_page)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("✅ Web server running on port 8080")
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("menu", start))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("🤖 Bot running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
