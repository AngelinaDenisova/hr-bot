import asyncio
import json
import time

import pytz
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
import db as db
from bot_buttons import time_data,cancel_job,confirm_job,jobs_reverse
from bot_texts import alert_user,admin_alert_send,jobs_answers
import datetime


config = json.load(open('config.json', 'rb'))
alert_chat_ids = {1:config["project_manager_chat_id"],
                  2:config["system_analytic_chat_id"],
                  3:config["devops_chat_id"],
                  4:config["qa_auto_chat_id"],
                  5:config["it_recruiter_chat_id"],
                  6:config["finance_manager_chat_id"]}


def get_username(user: db.User) -> str:
    return "@" + "Скрытый" if user.username is None else "@" + user.username


def get_user_link(user_id) -> str:
    return f"<a href='tg://user?id={user_id}'>ссылка</a>"


def calc_percent(user: db.User) -> int:
    return user.percent

def reply_kb_constructor(buttons:[str]):
    kb = ReplyKeyboardMarkup(keyboard=[],resize_keyboard=True)
    for buttons_row in buttons:
        buttons_temp = []
        for button in buttons_row:
            buttons_temp.append(KeyboardButton(text=button))
        kb.keyboard.append(buttons_temp)
    return kb

def get_cancel_kb(job_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cancel_job, callback_data=f'cancel:{job_id}')
        ]
    ])

def get_confirm_kb(job_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=confirm_job, callback_data=f'confirm:{job_id}')
        ],
        [
            InlineKeyboardButton(text=cancel_job, callback_data=f'cancel:{job_id}')
        ]
    ])

def get_time_btns(with_datetime=False):
    today = datetime.datetime.now(tz=pytz.timezone(config['timezone'])).today()
    day_of_week = today.weekday()

    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    result = []
    if with_datetime:
        datetime_objects = {}
    for i, day_name in enumerate(days):
        if day_name in time_data:
            days_from_today = i - day_of_week

            if days_from_today < 1:
                current_date = [today + datetime.timedelta(days=days_from_today + 7),days_from_today + 7]
            else:
                current_date = [(today + datetime.timedelta(days=days_from_today)), days_from_today]
            if with_datetime:
                datetime_objects[f"{day_name}({current_date[0].strftime('%d.%m')})"] = current_date[0]
            current_date[0] = f"{day_name}({current_date[0].strftime('%d.%m')})"

            result.append(current_date)
    result = [i[0] for i in sorted(result, key=lambda date: date[1])]
    if with_datetime:
        return result,datetime_objects
    else:
        return result

async def auto_checker():
    bot = get_bot()
    while True:
        try:
            await asyncio.sleep(5)
            jobs = await db.select_unalerted_interview()
            cur_ts = datetime.datetime.now(tz=pytz.timezone(config['timezone'])).timestamp()
            for job in jobs:
                if cur_ts < job.timestamp < cur_ts + (config['alert_before_hours'] * 60 * 60):
                    await bot.send_message(chat_id=job.user_id,
                                           text=alert_user.format(datetime.datetime.fromtimestamp(job.timestamp,
                                                tz=pytz.timezone(config['timezone'])).strftime('%H:%M')),
                                           reply_markup=get_confirm_kb(job.id))
                    user = await db.select_user_by_id(job.user_id)
                    await bot.send_message(chat_id=alert_chat_ids[job.job_id],
                                           text=admin_alert_send.format(datetime.datetime.fromtimestamp(job.timestamp,
                                                tz=pytz.timezone(config['timezone'])).strftime('%H:%M'),job.answers['0'],
                                                    f"@{user.username}"))

                    await db.set_alert_interview(job.id)
        except Exception as ex:
            print(f'CHECKER ERROR = {ex}')


def get_answers_text(job_id,answers:dict):
    result = jobs_reverse[job_id] + "\n\n"+ ('\n'.join([f"{jobs_answers[job_id][i]}\n-{j}"for i,j in answers.items()]))
    return result


def get_bot() -> Bot:
    return Bot(config["telegram_token"], default=DefaultBotProperties(parse_mode='HTML'), session=None)
