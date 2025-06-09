import sqlite3
import json
from config import load_config


JOBS_DATA_FROM_BUTTONS = {
    'Project Manager': 1,
    'Системный аналитик': 2,
    'DevOps-инженер': 3,
    'QA auto': 4,
    'IT-рекрутер': 5,
    'Финансовый менеджер': 6
}

PROJECT_MANAGER_ANSWERS = {
    1: {'Менее года': False, 'Год и более': True, '3 года и более': True},
    2: {'Не сталкивался': False, 'Agile и его фреймворки (Scrum, Kanban)': True, 'Waterfall': False, 'Все вышеперечисленные': True},
    3: {'1': False, '2-4': True, '5 и более': True},
    4: {'1-4': False, '5-15': True, '15 и более': True},
    5: {'до 100к': False, '100-150к': True, '150к и более': False},
}
SYSTEM_ANALYTIC_ANSWERS = {
    1: {'Менее года': False, 'Год и более': False, '3 года и более': True},
    2: {'Junior': False, 'Middle': True, 'Senior': True, 'Lead': False},
    3: {'Занимаюсь только системным анализом': False, '50/50 (fullstack)': True, 'Больше занимаюсь системным анализом': True, 'Больше занимаюсь бизнес-анализом': False},
    4: {'Нет, этим обычно занимался другой специалист': False, 'Участвовал в процессе, но это было не моя зона ответственности': False, 'Да, я проектировал архитектуру': True},
    5: {'до 200к': True, '200-250к': False, '250к и более': False}
}
DEVOPS_ANSWERS = {
    1: {'Менее года': False, 'Год и более': False, '3 года и более': True},
    2: {'Junior': False, 'Middle': True, 'Senior': True, 'Lead': False},
    3: {'Да, реализовал не один проект с этой БД': True, 'Есть только теоретическое понимание, в проектах с ней не сталкивался': False, 'Нет опыта': False},
    4: {'Нет': False, 'Стандартно - Python/Bash': True, 'Знаю другие языки': True},
    5: {'до 250к': True, '250-350к': True, '350к и более': False},
}
QA_AUTO_ANSWERS = {
    1: {'Менее года': False, 'Год и более': False, '3 года и более': True},
    2: {'Junior': False, 'Middle': True, 'Senior': True, 'Lead': False},
    3: {'Нет, занимаюсь веб-тестированием': False, 'Есть опыт написания автотестов для Android на других языках': True, 'Да, есть опыт': True},
    4: {'Писал самостоятельно': True, 'Запускал готовые': False, 'Приходилось заниматься и тем, и тем': True},
    5: {'до 150к': True, '150-200к': True, '200к и более': True},
}
IT_RECRUITER_ANSWERS = {
    1: {'Менее года':False, 'Год и более':True, '3 года и более':True},
    2: {'Массовые позиции (менеджеры по продажам, специалисты поддержки и т.д)':False, 'IT-специалисты':True, 'Точечный подбор, линейный персонал':True},
    3: {'Не работала в CRM':False, 'Хантфлоу, E-staff':True, 'Специализированная CRM компании':True},
    4: {'только hh':False, 'hh и авито':False, 'hh, тг-каналы, специализированные сайты для поиска IT-специалистов':True},
    5: {'до 100к': True, '100-150к': False, '250к и более': False}, # Note: salary ranges might need review for consistency if "250k и более" means strictly more. Assuming it means >= 250k.
}
FINANCE_MANAGER_ANSWERS = {
    1: {'Менее года': False, 'Год и более': False, '3 года и более': True},
    2: {'Нет понимания и опыта': False, 'Нет опыта, но есть понимание': True, 'Есть опыт работы в отрасли': True},
    3: {'Да, уверенный пользователь': True, 'Да, был небольшой опыт': True, 'Нет опыта': False},
    4: {'Да, умею пользоваться простыми формулами': False, 'Да, использую в работе именованные диапазоны, сложные формулы и другие функции': True, 'Нет, не умею': False},
    5: {'до 100к': True, '100-150к': False, '150к и более': False},
}

# Map job ID to its answer structure
JOB_ID_TO_ANSWERS_STRUCTURE = {
    1: PROJECT_MANAGER_ANSWERS,
    2: SYSTEM_ANALYTIC_ANSWERS,
    3: DEVOPS_ANSWERS,
    4: QA_AUTO_ANSWERS,
    5: IT_RECRUITER_ANSWERS,
    6: FINANCE_MANAGER_ANSWERS,
}

# From bot_texts.py (questions and infos)
PROJECT_MANAGER_QUESTIONS_TEXT = {
    1: 'Какой у тебя опыт на позиции Project Manager в компании занимающейся разработкой  веб-сайтов и мобильных приложений:',
    2: 'С какими методологиями управления проектами сталкивался в работе?',
    3: 'Какое максимальное количество проектов было в работе одновременно?',
    4: 'Сколько человек, в среднем, находилось под твоим управлением?',
    5: 'Вакансии с какой зарплатной вилкой сейчас рассматриваешь?',
}
PROJECT_MANAGER_INFO = '''Обязанности:
Управление проектами по разработке веб-сайтов и мобильных приложений от инициализации до завершения;
Взаимодействие с клиентами, сбор и анализ требований, консолидировать информацию в брифинг;
Планирование, распределение задач и контроль выполнения работы команды разработчиков, дизайнеров и тестировщиков;
Мониторинг соблюдения сроков и бюджета проекта;
Управление рисками, обеспечение бесперебойной коммуникации внутри команды и с клиентом;
Проведение встреч с командой (стендапы, ретроспективы, планирование), регулярная отчетность перед клиентами и руководством;
Контроль качества итогового продукта,;
Участие в оценке трудозатрат и стоимости проектов;
Составление/согласование смет, ведение документооборота по проектам.
Требования:
Опыт работы Project Manager в компании занимающейся разработкой веб-сайтов и мобильных приложений не менее 1 года;
Знание методов управления проектами (Agile, Scrum, Waterfall);
Понимание технических аспектов разработки сайтов и мобильных приложений;
Опыт работы с инструментами для управления проектами (Jira, Trello, Asana и т.п.);
Развитые навыки коммуникации, умение находить общий язык с командой и клиентами;
Способность одновременно вести несколько проектов;
Умение работать в условиях многозадачности и сжатых сроков;
Высокий уровень самоорганизации и ответственности;
Условия:
Возможность трудоустройства в аккредитованную IT-компанию, подходящую для получения IT-ипотеки и предоставляющую отсрочку от призыва на военную службу;
Гибкие рабочие процессы и разумное управление;
Минимум бюрократии и отсутствие строгого контроля: мы не фиксируем действия на экране и деликатно отслеживаем рабочее время в Jira;
Открытость в общении и задачах с минимумом бюрократии;
Создание твоего личного плана развития в рамках компании;
Регулярное повышение заработной платы'''

SYSTEM_ANALYTIC_QUESTIONS_TEXT = {
    1: 'Сколько лет занимаешься системным анализом?',
    2: 'К какому грейду себя относишь?',
    3: 'Какое соотношение системного к бизнес-анализу в твоей работе?',
    4: 'Есть ли опыт проектирования архитектуры?',
    5: 'Вакансии с какой зарплатной вилкой сейчас рассматриваешь?'
}
SYSTEM_ANALYTIC_INFO = '''Чем предстоит заниматься:
Участие в переговорах с заказчиком, выявление и оформление требований;
Разработка совместно с командой проекта функциональных и нефункциональных требований, в том числе:
проектирование и описание пользовательских сценариев;
проектирование и описание клиент-серверного взаимодействия;
участие в проектировании архитектуры решения;
проектирование и описание серверной логики.
Участие в развитии проекта:
формирование и управление бэклогом;
предложение гипотез по развитию проекта.
Что мы ожидаем от нашего кандидата:
Опыт работы системным аналитиком в Mobile / Web-проектах от 2х лет;
Опыт подготовки функциональных требований;
Опыт проектирования интеграций;
Системное мышление;
Умение оперативно переключаться между задачами;
Способность эффективно строить работу в ситуации неопределённости;
Умение находить компромисс и оптимальное решение и точно формулировать задачи.
Что мы предлагаем:
Возможность трудоустройства в аккредитованную IT-компанию, подходящую для получения IT-ипотеки и предоставляющую отсрочку от призыва на военную службу;
Гибкие рабочие процессы и разумное управление;
Минимум бюрократии и отсутствие строгого контроля: мы не фиксируем действия на экране и деликатно отслеживаем рабочее время в Jira;
Открытость в общении и задачах с минимумом бюрократии;
Создание твоего личного плана развития в рамках компании;
Регулярное повышение заработной платы;
Работа в центре Ростова-на-Дону или удаленно;
Отличный баланс work-life.
'''

DEVOPS_QUESTIONS_TEXT = {
    1: 'Сколько лет занимаешься администрированием Linux, MAC систем?',
    2: 'К какому грейду себя относишь?',
    3: 'Есть опыт работы с БД postgresql?',
    4: 'Можешь ли писать на каких-то языках программирования?',
    5: 'Вакансии с какой зарплатной вилкой сейчас рассматриваешь?'
}
DEVOPS_INFO = '''Требования:
Опыт работы с Git.
Опыт выстраивания процессов CI/CD.
Понимание микросервисной архитектуры.
Опыт работы с Docker и Kubernetes.
Навыки написания скриптов (bash, Ansible).
Опыт администрирования Linux/Unix, Windows Server.
Знание архитектуры и принципов функционирования современных web-приложений.
Понимание принципов построения и интеграции информационных систем и распределенных систем.
Опыт работы с REST и SOAP сервисами.
Опыт работы с базами данных MSSQL, Oracle, PostgreSQL и написание SQL-запросов.
Наличие опыта автоматизации бизнес-процессов и рутинных операций.
Чем предстоит заниматься:
Установка программного обеспечения на тестовых и боевых окружениях банка.
Разработка скриптов автоматизированного развертывания ПО.
Автоматизация процессов администрирования.
Создание конвейера непрерывного развертывания ПО на окружениях банка.
Развертывание и управление кластерами Spark, включая оптимизацию производительности и использование ресурсов.
Внедрение решений для мониторинга и ведения логов для кластера Spark.
Установка и настройка API Gateway (например, NGINX, Kong, Apigee), включая маршрутизацию, балансировку нагрузки и управление API.
Развертывание и настройка реляционных (PostgreSQL, MySQL) и NoSQL баз данных (MongoDB).
Будет плюсом:
Знание Python и PowerShell.
Опыт работы с OpenShift.
Знание TeamCity и Bitbucket приветствуется.
Опыт работы с PySpark и Scala.
Мы предлагаем:
Удобный гибкий график;
Работа в центре Ростова-на-Дону или удаленно;
Возможность трудоустройства в аккредитованную IT-компанию, подходящую для получения IT-ипотеки и предоставляющую отсрочку от призыва на военную службу;
Гибкие рабочие процессы и разумное управление;
Минимум бюрократии и отсутствие строгого контроля: мы не фиксируем действия на экране и деликатно отслеживаем рабочее время в Jira;
Открытость в общении и задачах с минимумом бюрократии;
Создание твоего личного плана развития в рамках компании;
Регулярное повышение заработной платы.
'''

QA_AUTO_QUESTIONS_TEXT = {
    1: 'Сколько лет занимаешься автоматизированным тестированием?',
    2: 'К какому грейду себя относишь?',
    3: 'Есть ли опыт написания автотестов для Android на Espresso или Kaspresso (Kotlin)',
    4: 'Писал тесты самостоятельно или запускал готовые?',
    5: 'Вакансии с какой зарплатной вилкой сейчас рассматриваешь?'
}
QA_AUTO_INFO = '''Обязанности:
Писать автотесты для мобильного и ТВ приложений (Marathon, Kakao и наша in-house тестовая система);
Писать и дорабатывать PageObject-ы для экранов;
Дорабатывать тестовую систему для поддержки новых элементов и взаимодействия с ними;
Дорабатывать тестовую инфраструктуру.
Требования:
Знание Kotlin;
Знание платформы Android;
Понимание как писать свои UI-элементы (Compose и View);
Работали с многомодульными проектами;
Владеете реактивным программированием (RxJava 2 и Flow);
Умеете применять dependency injection (Dagger 2);
Умение писать Unit-тесты;
Умение работать с оценками трудоемкости и требованиями (затраты времени и результат не должны быть неожиданностью для заказчика)
Будет плюсом:
Уже занимались UI-тестами;
Смотрели, что умеет Kotlin Multiplatform Mobile;
Базово знаете Bash, Ruby, Python или другие скриптовые языки программирования.
Условия:
Возможность трудоустройства в аккредитованную IT-компанию, подходящую для получения IT-ипотеки и предоставляющую отсрочку от призыва на военную службу;
Гибкие рабочие процессы и разумное управление;
Минимум бюрократии и отсутствие строгого контроля: мы не фиксируем действия на экране и деликатно отслеживаем рабочее время в Jira;
Открытость в общении и задачах с минимумом бюрократии;
Создание твоего личного плана развития в рамках компании;
Регулярное повышение заработной платы
'''

IT_RECRUITER_QUESTIONS_TEXT = {
    1: 'Сколько лет занимаешься рекрутингом?',
    2: 'Какие вакансии в основном были в работе?',
    3: 'С какими CRM есть опыт работы?',
    4: 'Какие каналы поиска использовала в работе?',
    5: 'Вакансии с какой зарплатной вилкой сейчас рассматриваешь?'
}
IT_RECRUITER_INFO = '''Требования:
Снятие портрета кандидата от команды заказчика;
Поиск кандидатов на специализированных площадках;
Грамотная устная и письменная речь, навыки продающих сообщений и писем;
Четкость и системность;
Понимание принципов IT разработки в целом и работы отдельных команд (Backend, Frontend, QA, DevOps);

Чем предстоит заниматься:
Поиск кандидатов;
Проведение первичных интервью, оценка soft skills, организация и посещение технических собеседований;
Активный поиск IT специалистов (Frontend, Backend, Mobile Developer, Project manager, Sales и другие);
Сопровождение кандидатов на всех этапах подбора (от запроса до вывода на проект). 
Составление резюме и сопроводительных писем;
Сопровождение кандидатов на интервью с клиентами (согласование слотов, проведение подготовительных звонков);
Согласование офферов, проведение переговоров;
Ведение базы кандидатов, отчетность по проделанной работе.

Будет плюсом:
Владение Хантфлоу;
Наличие опыта работы в оффлайне на конференциях и митапах
Мы предлагаем:
Удобный, гибкий график
Работа в центре Ростова-на-Дону или удаленно;
Отличный баланс work-life;
И самое главное – это лучшие люди вокруг.
Сильная команда;
Интересные проекты и сложные задачи;
Никакой бюрократии.
'''

FINANCE_MANAGER_QUESTIONS_TEXT = {
    1: 'Какой у тебя опыт на позиции Финансиста/экономиста/бухгалтера?',
    2: 'Есть ли понимание, как устроена сфера IT/опыт работы в этой отрасли?',
    3: 'Есть опыт работы с 1С?',
    4: 'Умеешь ли работать с Excel, Google-таблицами?',
    5: 'Вакансии с какой зарплатной вилкой сейчас рассматриваешь?'
}
FINANCE_MANAGER_INFO = '''Обязанности:
Контроль управленческого учета и помощь в его развитии;
Бюджетирование: на уровне компании и внутри группы компании;
Контроль ДДС, взаиморасчетов, управление дебиторской и кредиторской задолженностью, стратегическое и оперативное финансовое планирование;
Управленческая отчетность, анализ отклонений, сверка корректности предоставленных данных по часам выполненных работ и расчетов менеджеров по системе мотивации;
Расчет экономических моделей, создание финансовых инструментов для решения конкретных задач;
Работа с представителями банков и агентами по банковским гарантиям;
Взаимодействие с проектным и коммерческим отделами;
Своевременный контроль за достаточностью средств на разных счетах;
Подготовка платёжных документов в клиент-банке, проведение платежей;
Осуществление кассовых операций;
Составление и согласование платежного календаря.
Требования:
Опыт работы финансовым менеджером/аналитиком от 2-х лет;
Высшее образование (финансы / экономика);
Знания в области бюджетирования и планирования;
Способность качественно работать с большим объемом информации и документооборотом;
Знание гражданского, налогового, бухгалтерского законодательства, базовые знания расчета ФОТ;
Владение Excel (фильтры, формулы и пр.) на уровне продвинутого пользователя;
Умение организовывать и структурировать процесс работы.
Будет плюсом:
Знание основ Бухгалтерского учета и 1С Бухгалтерия 8.3.
Важные личностные качества:
Любовь к цифрам и внимательность;
Высокая степень личной ответственности;
Развитые коммуникативные качества, способность доносить и аргументировать свою позицию.
Условия:
Удобный гибкий график;
Работа в центре Ростова-на-Дону или удаленно;
Возможность трудоустройства в аккредитованную IT-компанию, подходящую для получения IT-ипотеки и предоставляющую отсрочку от призыва на военную службу;
Гибкие рабочие процессы и разумное управление;
Минимум бюрократии и отсутствие строгого контроля: мы не фиксируем действия на экране и деликатно отслеживаем рабочее время в Jira;
Открытость в общении и задачах с минимумом бюрократии;
Создание твоего личного плана развития в рамках компании;
Регулярное повышение заработной плат'''

# Map job ID to its question texts and info
JOB_ID_TO_TEXTS_AND_INFO = {
    1: {"questions": PROJECT_MANAGER_QUESTIONS_TEXT, "info": PROJECT_MANAGER_INFO},
    2: {"questions": SYSTEM_ANALYTIC_QUESTIONS_TEXT, "info": SYSTEM_ANALYTIC_INFO},
    3: {"questions": DEVOPS_QUESTIONS_TEXT, "info": DEVOPS_INFO},
    4: {"questions": QA_AUTO_QUESTIONS_TEXT, "info": QA_AUTO_INFO},
    5: {"questions": IT_RECRUITER_QUESTIONS_TEXT, "info": IT_RECRUITER_INFO},
    6: {"questions": FINANCE_MANAGER_QUESTIONS_TEXT, "info": FINANCE_MANAGER_INFO},
}

DB_NAME = 'V.sqlite3'

def _create_tables(cursor):
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
    print("Tables checked/created.")

async def populate_all():
    # Load config using the new function
    config = load_config()
    superadmin_id = config.SUPERADMIN_USER_ID

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    _create_tables(cursor) # Ensure tables exist

    # Add Superadmin if SUPERADMIN_USER_ID is set and is an integer
    if superadmin_id and isinstance(superadmin_id, int):
        try:
            # Ensure the user exists in the users table first (important for FOREIGN KEY)
            cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
                           (superadmin_id, "superadmin_placeholder")) # Username can be updated later by bot
            
            cursor.execute("INSERT OR REPLACE INTO admins (user_id, role) VALUES (?, ?)",
                           (superadmin_id, 'superadmin'))
            print(f"Superadmin with ID {superadmin_id} ensured/updated.")
        except sqlite3.Error as e:
            print(f"Error adding/updating superadmin: {e}")
    elif superadmin_id:
        print(f"SUPERADMIN_USER_ID in config.json is not a valid integer: {superadmin_id}. Superadmin not added.")
    else:
        print("SUPERADMIN_USER_ID not found or is null in config.json. Superadmin not added.")

    # Removed global deletion of job-related data to preserve admin-added jobs.
    # Deletions will now be targeted per predefined job.
    # print("Clearing existing job-related data from jobs, questions, answer_options...")
    # cursor.execute("DELETE FROM answer_options") # Global delete removed
    # cursor.execute("DELETE FROM questions")    # Global delete removed
    # cursor.execute("DELETE FROM jobs")         # Global delete removed
    # conn.commit()
    # print("Cleared existing job-related data.")

    # Populate/Update predefined jobs, their questions, and answer_options
    for job_name, job_id in JOBS_DATA_FROM_BUTTONS.items():
        description = JOB_ID_TO_TEXTS_AND_INFO[job_id]["info"]
        
        print(f"Processing predefined job ID {job_id} ('{job_name}')...")

        # Delete existing questions and answer options for THIS predefined job_id first
        try:
            # Get question_ids for the current job_id to delete their answer_options
            cursor.execute("SELECT id FROM questions WHERE job_id = ?", (job_id,))
            question_ids_tuples = cursor.fetchall()
            if question_ids_tuples:
                question_ids = [qid[0] for qid in question_ids_tuples]
                placeholders = ",".join("?" for _ in question_ids)
                print(f"  Deleting answer options for question IDs: {question_ids} (job ID: {job_id})")
                cursor.execute(f"DELETE FROM answer_options WHERE question_id IN ({placeholders})", question_ids)
            
            print(f"  Deleting questions for job ID: {job_id}")
            cursor.execute("DELETE FROM questions WHERE job_id = ?", (job_id,))
            
            # Insert or replace the job itself. This updates name/description if ID exists.
            print(f"  Inserting/Replacing job ID: {job_id} with name: '{job_name}'")
            cursor.execute("INSERT OR REPLACE INTO jobs (id, name, description) VALUES (?, ?, ?)",
                           (job_id, job_name, description))
            conn.commit() # Commit after each job's cleanup and replace

        except sqlite3.Error as e:
            print(f"  Error during cleanup/replacement for job ID {job_id}: {e}")
            conn.rollback() # Rollback changes for this job if error occurs
            continue # Skip to next predefined job

        # Populate questions and answer_options tables for this job_id
        question_texts = JOB_ID_TO_TEXTS_AND_INFO[job_id]["questions"]
        answer_structures = JOB_ID_TO_ANSWERS_STRUCTURE[job_id]

        for order_num, question_text in question_texts.items():
            try:
                print(f"    Inserting question order {order_num} for job ID {job_id}...")
                cursor.execute("INSERT INTO questions (job_id, text, order_num) VALUES (?, ?, ?)",
                               (job_id, question_text, order_num))
                question_db_id = cursor.lastrowid

                if order_num in answer_structures:
                    for answer_text, is_correct in answer_structures[order_num].items():
                        cursor.execute("INSERT INTO answer_options (question_id, text, is_correct) VALUES (?, ?, ?)",
                                       (question_db_id, answer_text, is_correct))
                conn.commit() # Commit after adding each question and its options
            except sqlite3.Error as e: # Changed from IntegrityError to broader sqlite3.Error
                 print(f"    Error inserting question/options for job ID {job_id}, order {order_num}: {e}")
                 conn.rollback() # Rollback this question/options if error

    conn.commit() # Final commit
    conn.close()
    print("Database populated successfully!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(populate_all()) 
