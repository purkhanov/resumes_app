from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .gemeni import create_promprts, gather_prompt_tasks
from .elastic_search import get_resumes


app = FastAPI()
app.mount("/static", StaticFiles(directory = "static"), name = "static")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)


@app.get("/ping")
async def read_root():
    return "pong"


@app.get("/search")
async def read_item(vacancy: str):
    serach_res = await get_resumes(vacancy)
    total = serach_res["total"]
    resumes = serach_res["resumes"]
    promts = create_promprts(vacancy, resumes)
    result = await gather_prompt_tasks(promts)

    return {"total": total, "data": result}
    