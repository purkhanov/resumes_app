from aiohttp import ClientSession
import requests


# base_url = "http://localhost:9200"
base_url = "http://elastic_search:9200"


async def get_resumes(vacancy: str):
    promt = {
        "query": {
            "match": {
                "resume": vacancy
            }
        }
    }

    async with ClientSession(base_url = base_url) as session:
        result = {}

        async with session.post(url = "/resumes/_search", json = promt) as request:
            data = await request.json()

        result["total"] = data["hits"]["total"]["value"]

        resumes = []
        for resume in data["hits"]["hits"]:
            r = resume["_source"]
            resumes.append(r)

        result["resumes"] = resumes
        return result


def create_index(index_name):
    url = base_url + "/" + index_name

    data = {
        "mappings": {
            "properties": {
                "resume": {
                    "type": "text",
                    "analyzer": "russian"
                },
                "url_to_resume": {
                    "type": "text"
                }
            }
        }
    }

    res = requests.put(url = url, json = data)

    if res.ok:
        print("index created successfuly")
        print(res.json())
    else:
        print("error")
        print(res.json())


def add_to_elastic(index_name, resume, link_to_resume):
    url = f"{base_url}/{index_name}/_doc"
    data = {
        "resume": resume,
        "url_to_resume": link_to_resume
    }

    return requests.post(url = url, json = data)
