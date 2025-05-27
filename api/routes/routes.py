from fastapi import APIRouter
from database.pydantic import ChatRequest
from database.storage import chat_histories
from datetime import datetime
from fastapi.responses import JSONResponse
from api.function.embeddings_function import Embeddings
from api.function.requests import Database


router = APIRouter(tags=['Main'])


@router.post("/chat")
async def chat(request: ChatRequest):
    chat_id = request.chat_id
    question = request.question
    source = request.source
    now = datetime.now()
    history = chat_histories.get(chat_id, {}).get("history")
    result = await Embeddings.load_1all_embeddings_from_folder(question,history,chat_id,now)

    if chat_id not in chat_histories:
        chat_histories[chat_id] = {
            "history": [],
            "last_active": now,
            "lid_name": source
        }

    chat_histories[chat_id]["history"].append(("user", question))
    chat_histories[chat_id]["last_active"] = str(now)

    # Место, где ты вызываешь ИИ:
    answer = result["answer"]

    chat_histories[chat_id]["history"].append(("bot", answer))

    if result["value"]:
        value = result["value"]
        last_active = chat_histories.get(chat_id, {}).get("last_active")
        history = chat_histories.get(chat_id, {}).get("history")
        try:
            await Database.set_chat(history,chat_id,value,last_active,source)
        except Exception as e:
            print(f"Не получилось сохранить данные чата:{chat_id}")
        try:
            Database.send_lead_to_crm(value,history,source)
        except Exception as e:
            print(f"Не получилось отправить лид в CRM: {e}")


    return {"answer": answer,
            "value":result["value"],
            "time_total": result["metrics"]["total_time_sec"],
            "time_ai":result["metrics"]["openai_time_sec"],
            "time_search":result["metrics"]["search_time_sec"]
            }

@router.get("/chat_histories")
async def get_chat_histories():
    return JSONResponse(content=chat_histories)
