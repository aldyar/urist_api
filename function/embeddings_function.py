import os
import json
from openai import AsyncOpenAI
import time
from config import AI_TOKEN ,PROXY
import httpx
from function.requests import Database
import tiktoken
import numpy as np
from numpy.linalg import norm
from database.models import async_session

proxy_url = PROXY

transport = httpx.AsyncHTTPTransport(proxy=proxy_url)

client = AsyncOpenAI(
    api_key=AI_TOKEN
    ,http_client=httpx.AsyncClient(transport=transport)
)
encoding = tiktoken.encoding_for_model("gpt-4-turbo")


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


class Embeddings:
    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))


    async def get_openai_embedding(text: str) -> list[float]:
        total_tokens_used = 0
        total_cost_usd = 0.0
    # Подсчёт токенов
        encoding = tiktoken.encoding_for_model("text-embedding-3-small")
        num_tokens = len(encoding.encode(text))

        # Стоимость: $0.00002 за 1k токенов
        cost = (num_tokens / 1000) * 0.00002

        # Обновляем общую статистику
        total_tokens_used += num_tokens
        total_cost_usd += cost
        print(f'TOKENS:__________{total_tokens_used}')
        print(f'COST:___________{total_cost_usd}')
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        result =  response.data[0].embedding
        return result
    

    async def load_1all_embeddings_from_folder(question: str,history,chat_id,last_active):
        config = await Database.get_config()
        full_time_start = time.time()
        all_texts = []
        all_embeddings = []

        folder_path = "files"

        # Загружаем все тексты и эмбеддинги из JSON-файлов
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        all_texts.append(item["text"])
                        all_embeddings.append(item["embedding"])

        # Получаем эмбеддинг вопроса
        search_start = time.time()
        question_embedding = await Embeddings.get_openai_embedding(question)
        

        # Считаем схожесть вопроса с каждым текстом
        similarities = [
            Embeddings.cosine_similarity(question_embedding, emb)
            for emb in all_embeddings
        ]
        search_time = time.time() - search_start
        # Сортируем по схожести и берём топ-N
        top_n = 3
        top_results = sorted(
            zip(similarities, all_texts),
            key=lambda x: x[0],
            reverse=True
        )[:top_n]

        # Формируем контекст
        context = "\n\n".join([
            f"[Фрагмент {i+1}] (Схожесть: {score:.3f})\n{text}"
            for i, (score, text) in enumerate(top_results)
        ])

        # Собираем сообщение
        system_content = config.role
        user_content = (
    f"История диалога:\n{history}\n\n"
    f"Сообщение от пользователя:\n{question}\n\n"
    f"База знаний, которую можно использовать в ответе:\n{context}\n\n"
    f"{config.prompt}\n\n"
    f"Если в сообщении пользователя есть контактный номер телефона, пожалуйста, верни JSON в следующем формате:\n"
    f'{{"answer": "<твой ответ>", "contact": "<номер или null или false>"}}\n\n'
    f"- Если номер телефона найден — укажи его в поле `contact`.\n"
    f"- Если номер не найден — верни `null`.\n"
    f"- Если пользователь попрощался или диалог логически завершён — верни `false` в поле `contact`.\n"
    f"Не пиши ничего, кроме JSON."
)

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        openai_start = time.time()
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2
        )
        openai_time = time.time() - openai_start
        response_text =  response.choices[0].message.content
        try:
            parsed = json.loads(response_text)
            answer = parsed.get("answer", "")
            value = parsed.get("contact", None)
        except json.JSONDecodeError:
            # Если вдруг GPT не вернул JSON, обрабатываем fallback
            answer = response_text
            value = None
        if value:
            print(f'VALUE:_________{value}')
            #await Database.set_chat(history,chat_id,value,last_active)
        full_time = time.time() - full_time_start
        # Подсчёт символов и токенов в промпте
        prompt_chars = len(system_content) + len(user_content)
        prompt_tokens = len(encoding.encode(system_content)) + len(encoding.encode(user_content))
        response_chars = len(answer)
        response_tokens = len(encoding.encode(answer))

        # Подсчёт стоимости
        input_cost = (prompt_tokens / 1000) * 0.01
        output_cost = (response_tokens / 1000) * 0.03
        total_cost = input_cost + output_cost

        full_time = time.time() - full_time_start
        return {
                    "answer": answer,
                    "context": context,
                    "value": value,
                    "metrics": {
                        "prompt_chars": prompt_chars,
                        "prompt_tokens": prompt_tokens,
                        "response_chars": response_chars,
                        "response_tokens": response_tokens,
                        "input_cost_usd": input_cost,
                        "output_cost_usd": output_cost,
                        "total_cost_usd": total_cost,
                        "search_time_sec": search_time,
                        "openai_time_sec": openai_time,
                        "total_time_sec": full_time
                            }
                }