import logging
import csv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Файл для сохранения записей
RECORD_FILE = 'appointments.csv'
# ID администратора (замените на ваш ID)
ADMIN_ID = 2065772283

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот для записи на стрижку. Выберите дату и время.')
    await show_dates(update, context)

# Показать доступные даты
async def show_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    today = datetime.today()
    keyboard = [[InlineKeyboardButton((today + timedelta(days=i)).strftime('%Y-%m-%d'), callback_data=(today + timedelta(days=i)).strftime('%Y-%m-%d'))] for i in range(7)]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text('Выберите дату:', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Выберите дату:', reply_markup=reply_markup)

# Обработчик выбора даты
async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    selected_date = query.data
    context.user_data['selected_date'] = selected_date
    await query.answer()

    await show_times(update, context, selected_date)

# Показать доступные временные слоты
async def show_times(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_date: str) -> None:
    times = ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    keyboard = [[InlineKeyboardButton(time, callback_data=time)] for time in times]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(f'Вы выбрали {selected_date}. Теперь выберите время:', reply_markup=reply_markup)

# Обработчик выбора времени
async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    selected_time = query.data
    selected_date = context.user_data.get('selected_date')
    user = update.effective_user
    await query.answer()
    
    await update.callback_query.message.reply_text(f'Вы успешно записались на стрижку на {selected_date} в {selected_time}.')

    # Сохраняем запись в файл
    save_appointment(user, selected_date, selected_time)

# Функция для сохранения записи в файл
def save_appointment(user, date, time):
    with open(RECORD_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([user.id, user.username, user.full_name, date, time])

# Обработчик команды /admin для просмотра всех записей
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text('У вас нет прав для использования этой команды.')
        return

    # Чтение записей из файла
    records = read_appointments()
    if not records:
        await update.message.reply_text('Нет записей.')
        return

    # Форматирование записей для отправки
    response = 'Записи на стрижку:\n'
    for record in records:
        response += f'ID: {record[0]}, Username: {record[1]}, Full Name: {record[2]}, Date: {record[3]}, Time: {record[4]}\n'

    await update.message.reply_text(response)

# Функция для чтения записей из файла
def read_appointments():
    try:
        with open(RECORD_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            return list(reader)
    except FileNotFoundError:
        return []

def main() -> None:
    # Вставьте сюда свой токен API
    application = Application.builder().token("7263390201:AAEGwJtMqlVAy7SmYhNjlVsbL-ni8BqFzmM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(select_date, pattern=r'^\d{4}-\d{2}-\d{2}$'))
    application.add_handler(CallbackQueryHandler(select_time, pattern=r'^\d{2}:\d{2}$'))
    application.add_handler(CommandHandler("admin", admin))

    application.run_polling()

if __name__ == '__main__':
    main()
