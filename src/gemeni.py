import asyncio
import re
import json
from aiohttp import ClientSession


gemeni_api = ""
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemeni_api}"
headers = {"Content-Type": "application/json"}
static = "/static/resumes/"


def create_promprt(vacancy, resume: str):
    prompt = f"""
    Задача: Оценить, насколько кандидат подходит для представленной вакансии, 
    на основе информации из его резюме. Оценка должна включать процент соответствия, 
    отметку "Подходит" или "Не подходит" и выделение ключевых навыков и опыта, подтверждающих соответствие.
    Ответ должен быть структурирован в виде ключ-значение:
    {{
        "full_name": "Имя Фамилия",
        "birth_date": "DD-MM-YY, возраст",
        "country": "Страна и город проживания",
        "education": "Образование",
        "percent_appropriate": "Процент соответствия",
        "conformity_assessment": "Подходит или Не подходит",
        "experience": "Описание опыта работы, связанного с вакансией",
        "high_skills": "Ключевые навыки, подтверждающие соответствие"
    }}
    Вакансия: {vacancy}
    Резюме кандидата: {resume}
    Пример заполненного ответа:
    {{
        "full_name": "Абай Кунанбай",
        "birth_date": "01-01-1990, 34 года",
        "country": "Казахстан, Алматы",
        "education": "Высший, МУИТ"
        "percent_appropriate": "85%",
        "conformity_assessment": "Подходит",
        "experience": "Опыт работы в веб-разработке более 5 лет, включает проекты на Python и Django.",
        "high_skills": "Python, Django, REST API, Docker, PostgreSQL"
    }}
    """

    data = {
        "contents": [
                {"parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    return data


def create_promprts(vacancy: str, resumes: list):
    """
    Generates prompts based on a vacancy description and a list of resumes.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
        - "prompt": A dictionary with a nested structure representing the prompt, specifically:
        [
          {
            "contents": [
              {
                "parts": [
                  {"text": prompt_text}
                ]
              }
            ]
          }
        ]
        - "resume_link": The URL link to the associated resume (str).
    """

    promts = []
    for resume in resumes:
        prompt = create_promprt(vacancy, resume["resume"])
        promts.append(
            {
                "prompt": prompt,
                "resume_link": resume["url_to_resume"]
            }
        )

    return promts


async def create_task(session: ClientSession, promt: dict):
    _promt = promt["prompt"]
    async with session.post(url = url, json = _promt) as request:
        result = await request.json()
        result["resume_link"] = promt["resume_link"]
        return result
        

async def create_tasks(session: ClientSession, promts: str):
    tasks = []
    
    for promt in promts:
        task = asyncio.create_task(create_task(session, promt))
        tasks.append(task)
    
    return tasks


async def gather_prompt_tasks(promts: list):
    result = []

    async with ClientSession(headers = headers) as session:
        tasks = await create_tasks(session, promts)

        res_data = await asyncio.gather(*tasks)

    for res in res_data:
        resp = res["candidates"][0]["content"]["parts"][0]["text"]

        pattern = r"\{[^`]+\}"
        match = re.search(pattern, resp, re.DOTALL)

        if match:
            data = match.group()
        else:
            data = {"error"}

        data = json.loads(data)
        data["resume_link"] = res["resume_link"]
        
        result.append(data)
    
    return result
