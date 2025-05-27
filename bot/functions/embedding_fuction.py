import os
import json
#from sentence_transformers import SentenceTransformer, util
from openai import AsyncOpenAI
import time
from numpy.linalg import norm
import numpy as np
import tiktoken
from config import AI_TOKEN ,PROXY
import httpx
from bot.functions.requests import Database

proxy_url = PROXY

transport = httpx.AsyncHTTPTransport(proxy=proxy_url)

client = AsyncOpenAI(
    api_key=AI_TOKEN
    ,http_client=httpx.AsyncClient(transport=transport)
)
encoding = tiktoken.encoding_for_model("gpt-4-turbo")


class Embeddings:
    # async def load_all_embeddings_from_folder(question):
    #     model = SentenceTransformer("all-MiniLM-L6-v2")
    #       # <-- вставь свой ключ
    #     all_texts = []
    #     all_embeddings = []

    #     # Перебираем все файлы в указанной папке
    #     for filename in os.listdir("bot/files"):
    #         if filename.endswith(".json"):
    #             file_path = os.path.join("bot/files", filename)
    #             with open(file_path, "r", encoding="utf-8") as f:
    #                 data = json.load(f)

    #             # Добавляем тексты и эмбеддинги
    #             all_texts.extend(item["text"] for item in data)
    #             all_embeddings.extend(item["embedding"] for item in data)

    #     question_embedding = model.encode(question)

    #     # Считаем схожесть с каждым фрагментом
    #     cosine_scores = util.cos_sim(question_embedding, all_embeddings)[0]
    #     # Сортируем по убыванию схожести
    #     top_n = 3
    #     top_results = sorted(zip(cosine_scores, all_texts), key=lambda x: x[0], reverse=True)[:top_n]
    #     # Формируем контекст из топ-N фрагментов
    #     context = "\n\n".join([f"Фрагмент {i+1}:\n{t}" for i, (score, t) in enumerate(top_results)])

    #     messages = [
    #         {"role": "system", "content": "Ты юридический консультант. Отвечай кратко, юридически грамотно и по сути."},
    #         {"role": "user", "content": f"Вопрос: {question}\n\nВот выдержки из документа:\n{context}\n\nОтветь на вопрос на основе текста выше."}
    #     ]

    #     # Запрос к OpenAI (новый синтаксис)
    #     response = client.chat.completions.create(
    #         model="gpt-4-turbo",  # или "gpt-3.5-turbo"
    #         messages=messages,
    #         temperature=0.2
    #     )
    #     #elapsed_time = time.time() - start_time
    #     answer = response.choices[0].message.content
    #     return answer,context
    

    
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


    async def load_1all_embeddings_from_folder(question: str):
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
        user_content = f"Сообщение от пользователя: {question}\n\nБаза знаний которую можно использовать в ответе:\n{context}\n\n{config.prompt}"
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        openai_start = time.time()
        response = await client.chat.completions.create(
            model=config.gpt_model,
            messages=messages,
            temperature=0.2
        )
        openai_time = time.time() - openai_start
        answer =  response.choices[0].message.content
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
    
    def regenerate_embeddings(folder_path="files"):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                new_data = []
                for item in data:
                    text = item["text"]
                    embedding = Embeddings.get_openai_embedding(text)
                    new_data.append({"text": text, "embedding": embedding})

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=2)

                print(f"[✔] Перегенерирован файл: {filename}")

    # async def convert_txt_to_embeddings(file_path: str):
    #     if not file_path.endswith(".txt"):
    #         raise ValueError("Файл должен быть с расширением .txt")

    #     if not os.path.exists(file_path):
    #         raise FileNotFoundError(f"Файл {file_path} не найден")

    #     # Получаем имя файла без расширения и путь к директории
    #     folder = os.path.dirname(file_path)
    #     filename_wo_ext = os.path.splitext(os.path.basename(file_path))[0]
    #     output_path = os.path.join(folder, filename_wo_ext + ".json")

    #     new_data = []
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         for line in f:
    #             line = line.strip()
    #             if line:  # пропустить пустые строки
    #                 embedding = Embeddings.get_openai_embedding(line)
    #                 new_data.append({"text": line, "embedding": embedding})

    #     with open(output_path, "w", encoding="utf-8") as f:
    #         json.dump(new_data, f, ensure_ascii=False, indent=2)

    #     print(f"[✔] Конвертация завершена: {output_path}")
    async def convert_txt_to_embeddings_batched(file_path: str):
        batch_size=100
        if not file_path.endswith(".txt"):
            raise ValueError("Файл должен быть с расширением .txt")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")

        folder = os.path.dirname(file_path)
        filename_wo_ext = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(folder, filename_wo_ext + ".json")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        all_data = []

        for i in range(0, len(lines), batch_size):
            batch = lines[i:i+batch_size]
            
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )

            for text, res in zip(batch, response.data):
                all_data.append({"text": text, "embedding": res.embedding})

            print(f"[✔] Обработано {i+len(batch)} из {len(lines)} строк")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"[✔] Конвертация завершена: {output_path}")
        return output_path