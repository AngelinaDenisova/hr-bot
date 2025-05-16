ready_start = 'Готов отвечать на вопросы'
need_job_desc = 'Хочу почитать описание вакансии'
need_comp_desc = 'Хочу узнать о компании'

other_time = 'нет удобного времени'

cancel_job = 'отменить собеседование'
confirm_job = 'подтвердить собеседование'
back = 'Назад'

#### Project manager
project_manager = {
    1: {
        'Менее года': False,
        'Год и более': True,
        '3 года и более': True
    },
    2: {
        'Не сталкивался': False,
        'Agile и его фреймворки (Scrum, Kanban)': True,
        'Waterfall': False,
        'Все вышеперечисленные': True
    },
    3: {
        '1': False,
        '2-4': True,
        '5 и более': True
    },
    4: {
        '1-4': False,
        '5-15': True,
        '15 и более': True
    },
    5: {
        'до 100к': False,
        '100-150к': True,
        '150к и более': False
    },
}
#### Project manager

#### Finance manager
finance_manager = {
    1: {
        'Менее года': False,
        'Год и более': False,
        '3 года и более': True
    },
    2: {
        'Нет понимания и опыта': False,
        'Нет опыта, но есть понимание': True,
        'Есть опыт работы в отрасли': True
    },
    3: {
        'Да, уверенный пользователь': True,
        'Да, был небольшой опыт': True,
        'Нет опыта': False
    },
    4: {
        'Да, умею пользоваться простыми формулами': False,
        'Да, использую в работе именованные диапазоны, сложные формулы и другие функции': True,
        'Нет, не умею': False
    },
    5: {
        'до 100к': True,
        '100-150к': False,
        '150к и более': False
    },
}
#### Finance manager

#### DevOps
devops = {
    1: {
        'Менее года': False,
        'Год и более': False,
        '3 года и более': True
    },
    2: {
        'Junior': False,
        'Middle': True,
        'Senior': True,
        'Lead': False
    },
    3: {
        'Да, реализовал не один проект с этой БД': True,
        'Есть только теоретическое понимание, в проектах с ней не сталкивался': False,
        'Нет опыта': False
    },
    4: {
        'Нет': False,
        'Стандартно - Python/Bash': True,
        'Знаю другие языки': True
    },
    5: {
        'до 250к': True,
        '250-350к': True,
        '350к и более': False
    },
}
#### DevOps

#### QA auto
qa_auto = {
    1: {
        'Менее года': False,
        'Год и более': False,
        '3 года и более': True
    },
    2: {
        'Junior': False,
        'Middle': True,
        'Senior': True,
        'Lead': False
    },
    3: {
        'Нет, занимаюсь веб-тестированием': False,
        'Есть опыт написания автотестов для Android на других языках': True,
        'Да, есть опыт': True
    },
    4: {
        'Писал самостоятельно': True,
        'Запускал готовые': False,
        'Приходилось заниматься и тем, и тем': True
    },
    5: {
        'до 150к': True,
        '150-200к': True,
        '200к и более': True
    },
}
#### QA auto

#### System Analytic
system_analytic = {
    1: {
        'Менее года': False,
        'Год и более': False,
        '3 года и более': True
    },
    2: {
        'Junior': False,
        'Middle': True,
        'Senior': True,
        'Lead': False
    },
    3: {
        'Занимаюсь только системным анализом': False,
        '50/50 (fullstack)': True,
        'Больше занимаюсь системным анализом': True,
        'Больше занимаюсь бизнес-анализом': False
    },
    4: {
        'Нет, этим обычно занимался другой специалист': False,
        'Участвовал в процессе, но это было не моя зона ответственности': False,
        'Да, я проектировал архитектуру': True
    },
    5: {
        'до 200к': True,
        '200-250к': False,
        '250к и более': False
    }
}
#### System Analytic

#### IT Recruiter
it_recruiter = {
    1: {
        'Менее года':False,
        'Год и более':True,
        '3 года и более':True
    },
    2: {
        'Массовые позиции (менеджеры по продажам, специалисты поддержки и т.д)':False,
        'IT-специалисты':True,
        'Точечный подбор, линейный персонал':True
    },
    3: {
        'Не работала в CRM':False,
        'Хантфлоу, E-staff':True,
        'Специализированная CRM компании':True
    },
    4: {
        'только hh':False,
        'hh и авито':False,
        'hh, тг-каналы, специализированные сайты для поиска IT-специалистов':True
    },
    5: {
        'до 100к': True,
        '100-150к': False,
        '250к и более': False
    },
}
#### IT Recruiter

#### JOB NAMES
jobs = {'Project Manager':1,
'Системный аналитик':2,
'DevOps-инженер':3,
'QA auto':4,
'IT-рекрутер':5,
'Финансовый менеджер':6}
#### JOB NAMES
jobs_reverse = {j:i for i,j in jobs.items()}


#### TIME VAR REGEX

time_data = {
    "Понедельник": ['13:00', '15:00', '17:00'],
    "Вторник": ['10:00', '12:00', '13:00'],
    "Среда": ['11:00', '14:00'],
    "Четверг": ['12:30', '13:30', '16:30'],
    "Пятница": ['11:00', '14:00', '16:00']
}

#### TIME VAR REGEX



#### TOTAL JOBS ANSWERS BTNS JSON
jobs_answers  = {1:project_manager,
2:system_analytic,
3:devops,
4:qa_auto,
5:it_recruiter,
6:finance_manager}
#### TOTAL JOBS ANSWERS BTNS JSON
