import atexit
import json
import random
import sqlite3
import string
import time
from typing import NamedTuple, Optional, List

import aiosqlite


base_name = 'V.sqlite3'
with open('config.json', 'r') as file:
    config = json.loads(file.read())

class User(NamedTuple):
    id: int
    username: str


class Interview:
    def __init__(self,id,user_id,job_id,answers,timestamp,status,alerted):
        self.id: int = id
        self.user_id: str = user_id
        self.job_id:int = job_id
        self.answers:dict = json.loads(answers)
        self.timestamp:int = timestamp
        self.status:bool = status
        self.alerted:bool = alerted

async def create_user(user_id,username):
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute('INSERT INTO users(user_id, username) VALUES (?, ?)',
                    (user_id, username))
            await db.commit()
    except Exception as e:
        # print(f"Error in create_user: {e}")
        return None

async def select_user_by_id(user_id):
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT * FROM users WHERE user_id = ?',
                    (user_id,)) as cursor:
                res = await cursor.fetchone()
            if res is not None:
                return User(*res)
            else:
                # print(f"User not exist: {user_id}")
                return None
    except Exception as e:
        # print(f"Error in select_user: {e}")
        return None


async def create_interview(user_id,job_id,answers,timestamp,status):
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('INSERT INTO interviews(user_id,job_id,answers,timestamp,status) VALUES (?, ?, ?, ?, ?)',
                    (user_id,job_id,json.dumps(answers),timestamp,status)) as cursor:
                await db.commit()
                return cursor.lastrowid
    except Exception as e:
        # print(f"Error in create_interview: {e}")
        return None

async def cancel_interview_by_id(id):
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute('DELETE FROM interviews WHERE id = ?',
                    (id,))
            await db.commit()
    except Exception as e:
        # print(f"Error in cancel_interview: {e}")
        pass

async def select_interview_by_user_job_id(user_id,job_id):
    try:
        async with aiosqlite.connect(base_name) as db:
            async with  db.execute('SELECT * FROM interviews WHERE user_id = ? AND job_id = ?',
                    (user_id,job_id)) as cursor:
                res = await cursor.fetchone()
            if res is not None:
                return Interview(*res)
            else:
                # print(f"Interview not exist: {user_id}")
                return None
    except Exception as e:
        # print(f"Error in select_interview_by_user_job_id: {e}")
        return None

async def set_alert_interview(id):
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute('UPDATE interviews SET alerted = 1 WHERE id = ?',
                    (id,))
            await db.commit()
    except Exception as e:
        pass
        # print(f"Error in cancel_interview: {e}")

async def select_unalerted_interview():
    try:
        async with aiosqlite.connect(base_name) as db:
            async with  db.execute('SELECT * FROM interviews WHERE status = 1 AND alerted = 0') as cursor:
                res = await cursor.fetchall()
            return [Interview(*i) for i in res]
    except Exception as e:
        # print(f"Error in select_interview_by_user_job_id: {e}")
        return None


def _create():
    with sqlite3.connect(base_name, check_same_thread=False) as connection:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY NOT NULL,
                username       TEXT
            );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INT,
            job_id             INT,
            answers            TEXT,
            timestamp          INT,
            status             BOOL,
            alerted            BOOL DEFAULT 0
        );
        """)



_create()
