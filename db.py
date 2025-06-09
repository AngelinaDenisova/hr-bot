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
    username: Optional[str]


class Interview(NamedTuple):
    id: int
    user_id: int
    job_id: int
    answers: dict
    timestamp: int
    status: bool
    alerted: bool

async def create_user(user_id,username):
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute('INSERT INTO users(user_id, username) VALUES (?, ?)',
                    (user_id, username))
            await db.commit()
    except Exception as e:
        # print(f"Error in create_user: {e}")
        return None

async def add_user_if_not_exists(user_id: int, username: Optional[str]):
    """Adds a new user to the database or updates their username if they already exist."""
    try:
        async with aiosqlite.connect(base_name) as db:
            # Using INSERT OR REPLACE to add if new, or update username if user_id already exists
            await db.execute('INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)',
                           (user_id, username))
            await db.commit()
            # print(f"User {user_id} with username '{username}' ensured/updated.")
    except Exception as e:
        print(f"Error in add_user_if_not_exists (ensure_user_with_username): {e}")

async def select_user_by_id(user_id: int) -> Optional[User]:
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT user_id, username FROM users WHERE user_id = ?',
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
            async with  db.execute('SELECT id, user_id, job_id, answers, timestamp, status, alerted FROM interviews WHERE user_id = ? AND job_id = ?',
                    (user_id,job_id)) as cursor:
                res = await cursor.fetchone()
            if res is not None:
                # Deserialize answers from JSON string to dict
                return Interview(id=res[0], user_id=res[1], job_id=res[2], answers=json.loads(res[3]), timestamp=res[4], status=bool(res[5]), alerted=bool(res[6]))
            else:
                # print(f"Interview not exist: {user_id}")
                return None
    except Exception as e:
        # print(f"Error in select_interview_by_user_job_id: {e}")
        return None

async def select_interview_by_id(interview_id: int) -> Optional[Interview]:
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT id, user_id, job_id, answers, timestamp, status, alerted FROM interviews WHERE id = ?',
                                  (interview_id,)) as cursor:
                res = await cursor.fetchone()
            if res is not None:
                # Deserialize answers from JSON string to dict
                return Interview(id=res[0], user_id=res[1], job_id=res[2], answers=json.loads(res[3]), timestamp=res[4], status=bool(res[5]), alerted=bool(res[6]))
            else:
                return None
    except Exception as e:
        # print(f"Error in select_interview_by_id: {e}")
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
            async with  db.execute('SELECT id, user_id, job_id, answers, timestamp, status, alerted FROM interviews WHERE status = 1 AND alerted = 0') as cursor:
                rows = await cursor.fetchall()
            # Deserialize answers from JSON string to dict for each interview
            return [Interview(id=row[0], user_id=row[1], job_id=row[2], answers=json.loads(row[3]), timestamp=row[4], status=bool(row[5]), alerted=bool(row[6])) for row in rows]
    except Exception as e:
        # print(f"Error in select_unalerted_interview: {e}")
        return []

# New functions to fetch job data from the database
class Job(NamedTuple):
    id: int
    name: str
    description: Optional[str] = None

class AnswerOption(NamedTuple):
    id: int
    text: str
    is_correct: bool

class Question(NamedTuple):
    id: int
    job_id: int
    text: str
    order_num: int
    options: List[AnswerOption]

async def get_all_jobs() -> List[Job]:
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT id, name, description FROM jobs ORDER BY id') as cursor:
                rows = await cursor.fetchall()
            return [Job(*row) for row in rows]
    except Exception as e:
        # print(f"Error in get_all_jobs: {e}")
        return []

async def add_job(name: str, description: Optional[str] = "") -> Optional[int]:
    """Adds a new job to the database. Returns the ID of the new job or None on failure."""
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute("INSERT INTO jobs (name, description) VALUES (?, ?)",
                                  (name, description)) as cursor:
                await db.commit()
                return cursor.lastrowid
    except aiosqlite.IntegrityError:
        return None
    except Exception as e:
        return None

async def update_job_name(job_id: int, new_name: str) -> bool:
    """Updates the name of an existing job."""
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute("UPDATE jobs SET name = ? WHERE id = ?", (new_name, job_id))
            await db.commit()
            return db.changes > 0 # Returns True if a row was updated
    except aiosqlite.IntegrityError: # If new_name violates a UNIQUE constraint
        # print(f"Error updating job name for ID {job_id}: IntegrityError (e.g., name '{new_name}' already exists)")
        return False
    except Exception as e:
        # print(f"Error in update_job_name: {e}")
        return False

async def delete_job_and_associated_data(job_id: int) -> bool:
    """Deletes a job and all its associated questions and answer options."""
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute("PRAGMA foreign_keys = ON;") # Ensure foreign key constraints are active for cascading if set up
            # First, get all question IDs for the job to delete their answer options
            async with db.execute("SELECT id FROM questions WHERE job_id = ?", (job_id,)) as cursor:
                question_ids_tuples = await cursor.fetchall()
            
            question_ids = [qid[0] for qid in question_ids_tuples]

            if question_ids:
                # Create a string of placeholders for the IN clause
                placeholders = ",".join("?" for _ in question_ids)
                # Delete answer options for these questions
                await db.execute(f"DELETE FROM answer_options WHERE question_id IN ({placeholders})", question_ids)
            
            # Delete questions for the job
            await db.execute("DELETE FROM questions WHERE job_id = ?", (job_id,))
            
            # Delete the job itself
            await db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            
            await db.commit()
            # Check if the job was actually deleted to confirm success
            # This is a bit indirect; db.changes might reflect the last operation (job deletion)
            # A more robust check would be to try to fetch the job again.
            # For now, assuming success if no exceptions and commit happens.
            # If foreign keys with ON DELETE CASCADE were set up in table definitions for
            # questions (on job_id) and answer_options (on question_id), 
            # just deleting from 'jobs' would be enough if the DB supports it well.
            # Since we are doing it manually, this is a safer cross-SQLite-version approach.
            return True 
    except Exception as e:
        # print(f"Error deleting job {job_id} and associated data: {e}")
        # Consider rolling back if a transaction was explicitly started, though aiosqlite connection context might handle it.
        return False

async def get_job_details(job_id: int) -> Optional[Job]:
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT id, name, description FROM jobs WHERE id = ?', (job_id,)) as cursor:
                row = await cursor.fetchone()
            return Job(*row) if row else None
    except Exception as e:
        # print(f"Error in get_job_details: {e}")
        return None

async def get_questions_for_job(job_id: int) -> List[Question]:
    questions_map = {}
    try:
        async with aiosqlite.connect(base_name) as db:
            # Fetch all questions for the job
            async with db.execute('''
                SELECT q.id, q.job_id, q.text, q.order_num
                FROM questions q
                WHERE q.job_id = ?
                ORDER BY q.order_num
            ''', (job_id,)) as q_cursor:
                questions_data = await q_cursor.fetchall()

            if not questions_data:
                return []

            question_ids = [q_row[0] for q_row in questions_data]
            
            # Initialize questions in the map to preserve order and include those with no options
            for q_row in questions_data:
                questions_map[q_row[0]] = Question(id=q_row[0], job_id=q_row[1], text=q_row[2], order_num=q_row[3], options=[])

            # Fetch all answer options for these questions in one go
            # Create a string of placeholders for the IN clause
            placeholders = ','.join('?' for _ in question_ids)
            async with db.execute(f'''
                SELECT ao.id, ao.question_id, ao.text, ao.is_correct
                FROM answer_options ao
                WHERE ao.question_id IN ({placeholders})
            ''', question_ids) as o_cursor:
                options_data = await o_cursor.fetchall()

            # Populate options for each question
            for opt_row in options_data:
                option = AnswerOption(id=opt_row[0], text=opt_row[2], is_correct=bool(opt_row[3]))
                question_id_for_option = opt_row[1]
                if question_id_for_option in questions_map:
                    questions_map[question_id_for_option].options.append(option)
        
        # Return list of questions in the correct order
        return list(questions_map.values())
    except Exception as e:
        # print(f"Error in get_questions_for_job: {e}")
        return []

async def get_question_by_id(question_id: int) -> Optional[Question]:
    """Fetches a single question by its ID, including its answer options."""
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT id, job_id, text, order_num FROM questions WHERE id = ?', (question_id,)) as q_cursor:
                q_row = await q_cursor.fetchone()
            
            if not q_row:
                return None
            
            job_id = q_row[1] # We'll need job_id later if we want to go "back to questions list for this job"
            
            options = []
            async with db.execute('SELECT id, text, is_correct FROM answer_options WHERE question_id = ?', (question_id,)) as o_cursor:
                options_data = await o_cursor.fetchall()
            options = [AnswerOption(id=opt_row[0], text=opt_row[1], is_correct=bool(opt_row[2])) for opt_row in options_data]
            
            return Question(id=q_row[0], job_id=job_id, text=q_row[2], order_num=q_row[3], options=options)
    except Exception as e:
        # print(f"Error in get_question_by_id: {e}")
        return None

async def add_question_with_options(job_id: int, question_text: str, options_data: List[dict]) -> Optional[int]:
    """Adds a new question and its answer options to the database.
    options_data should be a list of dicts, e.g., [{"text": "Option 1", "is_correct": False}, ...]
    Returns the ID of the newly added question, or None on failure.
    """
    async with aiosqlite.connect(base_name) as db:
        try:
            # Determine the next order_num for this job_id
            async with db.execute('SELECT MAX(order_num) FROM questions WHERE job_id = ?', (job_id,)) as cursor:
                max_order_num_row = await cursor.fetchone()
            next_order_num = (max_order_num_row[0] if max_order_num_row and max_order_num_row[0] is not None else 0) + 1
            
            # Start transaction
            await db.execute("BEGIN TRANSACTION")
            
            # Insert the question
            async with db.execute('INSERT INTO questions (job_id, text, order_num) VALUES (?, ?, ?)',
                                  (job_id, question_text, next_order_num)) as cursor:
                question_id = cursor.lastrowid
            
            if not question_id:
                await db.execute("ROLLBACK")
                return None

            # Insert answer options
            for option in options_data:
                await db.execute('INSERT INTO answer_options (question_id, text, is_correct) VALUES (?, ?, ?)',
                               (question_id, option['text'], option['is_correct']))
            
            await db.execute("COMMIT")
            return question_id
        except Exception as e:
            await db.execute("ROLLBACK") # Ensure rollback on any error during the transaction
            # print(f"Error in add_question_with_options: {e}")
            return None

async def delete_question_and_options(question_id: int) -> bool:
    """Deletes a question and all its associated answer options from the database.
    Returns True on success, False on failure.
    """
    async with aiosqlite.connect(base_name) as db:
        try:
            await db.execute("BEGIN TRANSACTION")
            
            # Delete answer options first (due to foreign key constraint if any)
            await db.execute('DELETE FROM answer_options WHERE question_id = ?', (question_id,))
            
            # Then delete the question
            async with db.execute('DELETE FROM questions WHERE id = ?', (question_id,)) as cursor:
                if cursor.rowcount == 0: # Question not found
                    await db.execute("ROLLBACK")
                    # print(f"Question with id {question_id} not found for deletion.")
                    return False
            
            await db.execute("COMMIT")
            return True
        except Exception as e:
            await db.execute("ROLLBACK")
            # print(f"Error in delete_question_and_options: {e}")
            return False

async def update_question_text(question_id: int, new_text: str) -> bool:
    """Updates the text of a specific question."""
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('UPDATE questions SET text = ? WHERE id = ?', (new_text, question_id)) as cursor:
                await db.commit()
                return cursor.rowcount > 0 # Returns true if a row was updated
    except Exception as e:
        # print(f"Error in update_question_text: {e}")
        return False

async def update_question_options(question_id: int, new_options_data: List[dict]) -> bool:
    """Deletes all existing options for a question and adds new ones."""
    async with aiosqlite.connect(base_name) as db:
        try:
            await db.execute("BEGIN TRANSACTION")
            
            # Delete old options
            await db.execute('DELETE FROM answer_options WHERE question_id = ?', (question_id,))
            
            # Insert new options
            for option in new_options_data:
                await db.execute('INSERT INTO answer_options (question_id, text, is_correct) VALUES (?, ?, ?)',
                               (question_id, option['text'], option['is_correct']))
            
            await db.execute("COMMIT")
            return True
        except Exception as e:
            await db.execute("ROLLBACK")
            # print(f"Error in update_question_options: {e}")
            return False

class FormattedInterview(NamedTuple):
    interview_id: int
    user_id: int
    username: Optional[str]
    job_id: int
    job_name: str
    timestamp: int
    status: bool # Добавляем поле status для отладки и возможного использования

async def get_formatted_active_interviews() -> List[FormattedInterview]:
    """Fetches interviews that are considered active (timestamp in the future)
       and formats them with user and job names for admin display.
    """
    active_interviews = []
    current_unix_time = int(time.time())
    try:
        async with aiosqlite.connect(base_name) as db:
            # Select interviews with timestamp in the future, joining with users and jobs
            # Assuming interview.status = 0 means scheduled/not yet taken, status = 1 means completed.
            # We are interested in scheduled ones for management.
            # For now, timestamp > current_time is the primary filter for "active and manageable".
            sql = """
                SELECT i.id, i.user_id, u.username, i.job_id, j.name, i.timestamp, i.status
                FROM interviews i
                JOIN users u ON i.user_id = u.user_id
                JOIN jobs j ON i.job_id = j.id
                WHERE i.timestamp > ? AND i.status = 0 
                ORDER BY i.timestamp ASC
            """ 
            # Add other conditions like i.status != 'cancelled' if such status exists
            async with db.execute(sql, (current_unix_time,)) as cursor:
                rows = await cursor.fetchall()
            
            for row in rows:
                active_interviews.append(FormattedInterview(
                    interview_id=row[0],
                    user_id=row[1],
                    username=row[2],
                    job_id=row[3],
                    job_name=row[4],
                    timestamp=row[5],
                    status=bool(row[6]) # Add status, it will be 0 (False) due to WHERE clause
                ))
        return active_interviews
    except Exception as e:
        # print(f"Error in get_formatted_active_interviews: {e}")
        return []

async def get_formatted_past_interviews() -> List[FormattedInterview]:
    """Fetches interviews that are considered past (timestamp in the past) OR completed (status=1)
       and formats them with user and job names for admin display.
    """
    past_interviews = []
    current_unix_time = int(time.time())
    print(f"[DEBUG DB get_formatted_past_interviews] current_unix_time: {current_unix_time}") # Отладочный вывод

    try:
        async with aiosqlite.connect(base_name) as db:
            sql = """
                SELECT i.id, i.user_id, u.username, i.job_id, j.name, i.timestamp, i.status
                FROM interviews i
                LEFT JOIN users u ON i.user_id = u.user_id
                LEFT JOIN jobs j ON i.job_id = j.id
                WHERE (i.timestamp <= ? OR i.status = 1)
                ORDER BY i.timestamp DESC
            """
            async with db.execute(sql, (current_unix_time,)) as cursor:
                rows = await cursor.fetchall()
            
            print(f"[DEBUG DB get_formatted_past_interviews] Rows fetched from DB: {rows}") # Отладочный вывод

            for row in rows:
                username = row[2] if row[2] is not None else "(Пользователь не найден)"
                job_name = row[4] if row[4] is not None else "(Вакансия не найдена)"
                
                past_interviews.append(FormattedInterview(
                    interview_id=row[0],
                    user_id=row[1],
                    username=username, 
                    job_id=row[3],
                    job_name=job_name, 
                    timestamp=row[5],
                    status=bool(row[6]) # Добавляем статус
                ))
        print(f"[DEBUG DB get_formatted_past_interviews] Processed past_interviews: {past_interviews}") # Отладочный вывод
        return past_interviews
    except Exception as e:
        print(f"[ERROR DB get_formatted_past_interviews] Exception: {e}") # Можно оставить для логгирования ошибок
        return []

class AdminInterviewDetails(NamedTuple):
    interview: Interview # The full Interview object from db.py
    username: Optional[str]
    job_name: str

async def get_interview_details_for_admin(interview_id: int) -> Optional[AdminInterviewDetails]:
    """Fetches detailed information for a single interview for admin display,
       including the original Interview object, username, and job name.
    """
    try:
        interview_obj = await select_interview_by_id(interview_id) # Reuse existing function
        if not interview_obj:
            return None

        user = await select_user_by_id(interview_obj.user_id)
        job = await get_job_details(interview_obj.job_id)

        username = user.username if user else "N/A"
        job_name = job.name if job else "N/A"

        return AdminInterviewDetails(
            interview=interview_obj,
            username=username,
            job_name=job_name
        )
    except Exception as e:
        # print(f"Error in get_interview_details_for_admin: {e}")
        return None

async def update_interview_timestamp(interview_id: int, new_timestamp: int) -> bool:
    """Updates the timestamp of a specific interview."""
    try:
        async with aiosqlite.connect(base_name) as db:
            # We might also want to reset the 'alerted' status if the time changes
            # and it was previously alerted for an old time.
            # For now, just updating timestamp. Consider alerted status if it becomes relevant.
            async with db.execute('UPDATE interviews SET timestamp = ? WHERE id = ?',
                                  (new_timestamp, interview_id)) as cursor:
                await db.commit()
                return cursor.rowcount > 0 # True if a row was updated
    except Exception as e:
        # print(f"Error in update_interview_timestamp: {e}")
        return False

# Admin and role management functions
async def add_admin(user_id: int, role: str):
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute('INSERT OR REPLACE INTO admins (user_id, role) VALUES (?, ?)',
                           (user_id, role))
            await db.commit()
            return True
    except Exception as e:
        # print(f"Error in add_admin: {e}")
        return False

async def get_admin_role(user_id: int) -> Optional[str]:
    try:
        async with aiosqlite.connect(base_name) as db:
            async with db.execute('SELECT role FROM admins WHERE user_id = ?', (user_id,)) as cursor:
                res = await cursor.fetchone()
            return res[0] if res else None
    except Exception as e:
        # print(f"Error in get_admin_role: {e}")
        return None

async def remove_admin(user_id: int):
    try:
        async with aiosqlite.connect(base_name) as db:
            await db.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
            await db.commit()
            return True
    except Exception as e:
        # print(f"Error in remove_admin: {e}")
        return False

async def get_all_admins_by_role(target_role: str) -> List[User]:
    """Fetches all users who are admins with a specific role."""
    admins_list = []
    try:
        async with aiosqlite.connect(base_name) as db:
            # Join admins with users table to get user details in one query
            sql = """
                SELECT u.user_id, u.username
                FROM admins a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.role = ?
            """
            async with db.execute(sql, (target_role,)) as cursor:
                rows = await cursor.fetchall()
            
            for row in rows:
                admins_list.append(User(id=row[0], username=row[1])) # Map to User NamedTuple
        return admins_list
    except Exception as e:
        # print(f"Error in get_all_admins_by_role: {e}")
        return []

async def get_all_admin_and_recruiter_ids() -> List[int]:
    """Fetches all user_ids of users who are admins with role 'superadmin' or 'recruiter'."""
    user_ids = []
    try:
        async with aiosqlite.connect(base_name) as db:
            sql = """
                SELECT user_id
                FROM admins
                WHERE role = 'superadmin' OR role = 'recruiter'
            """
            async with db.execute(sql) as cursor:
                rows = await cursor.fetchall()
            user_ids = [row[0] for row in rows]
        return user_ids
    except Exception as e:
        # print(f"Error in get_all_admin_and_recruiter_ids: {e}")
        return []

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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id                 INTEGER PRIMARY KEY NOT NULL,
            name               TEXT NOT NULL,
            description        TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id             INTEGER NOT NULL,
            text               TEXT NOT NULL,
            order_num          INTEGER NOT NULL, -- To maintain question order for a job
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS answer_options (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id        INTEGER NOT NULL,
            text               TEXT NOT NULL,
            is_correct         BOOLEAN NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        );
        """)
        cursor.execute("""        CREATE TABLE IF NOT EXISTS admins (
            user_id        INTEGER PRIMARY KEY NOT NULL,
            role           TEXT NOT NULL, -- 'superadmin', 'recruiter'
            FOREIGN KEY (user_id) REFERENCES users(user_id) -- Опционально, для строгости
        );
        """)



_create()
