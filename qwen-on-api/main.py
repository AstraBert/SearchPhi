from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from textUtils import *
from chatHistoryUtils import PGClient, ConversationHistory
from dotenv import load_dotenv
import os
import random
from webSearch import *
from qdrantRag import SemanticCache, client, dense_encoder
from textUtils import text_inference
from fastapi.middleware.cors import CORSMiddleware
import time

load_dotenv()

pg_db = os.getenv("pgql_db")
pg_user = os.getenv("pgql_user")
pg_psw = os.getenv("pgql_psw")

pg_conn_str = f"postgresql://{pg_user}:{pg_psw}@localhost:5432/{pg_db}"
pg_client = PGClient(pg_conn_str)

usr_id = random.randint(1,10000)
convo_hist = ConversationHistory(pg_client, usr_id)
convo_hist.add_message(role="system", content="You are a web-powered assistant. You have to answer the user based on their prompt and on the web-provided context you will receive.")

semantic_cache = SemanticCache(client, dense_encoder, "semantic_cache")

app = FastAPI(
    docs_url=None,
    title="SupaSeqs - Swagger UI",
    description="Manage your DNA sequences databases with the power of PostgreSQL",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SupaSeqs - Swagger UI",
        swagger_favicon_url="/static/favicon.png",
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}



@app.get("/messages/{message}")
async def read_item(message: str):
    semantic_answer = semantic_cache.search_cache(message)
    if semantic_answer:
        return JSONResponse(content={"response": semantic_answer}, status_code=200)
    else:
        results = web_search(message)
        await results_to_db(results)
        context = search_db(message)
        convo_hist.add_message("user", message)
        convo_hist.add_message("user", f"This is the context to answer the my prompt:\n\n{context}")
        response = text_inference(convo_hist)
        response = response.replace("<|im_end|>","")
        semantic_cache.upload_to_cache(message, response)
        return JSONResponse(content={"response": response}, status_code=200)
    