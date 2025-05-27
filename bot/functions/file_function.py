from docx import Document
import fitz
#from sentence_transformers import SentenceTransformer
import json
import os


class File:

    async def docx_to_txt(file_path):
        doc = Document(file_path)  # Открываем .docx файл
        text = "\n".join([p.text for p in doc.paragraphs])  # Собираем весь текст
        txt_path = file_path.replace('.docx', '.txt')  # Создаём путь с тем же именем, но .txt
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)  # Записываем текст в файл
        return txt_path  # Возвращаем путь к .txt
    

    async def pdf_to_txt(file_path):
        doc = fitz.open(file_path)  # Открываем PDF-файл
        text = ""
        for page in doc:
            text += page.get_text() + "\n"  # Извлекаем текст со страницы
        doc.close()

        txt_path = file_path.replace('.pdf', '.txt')  # Заменяем расширение на .txt
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)  # Сохраняем текст в файл

        return txt_path  # Возвращаем путь к сохранённому текстовому файлу
    
    
    # async def txt_to_embenddings(file_path):
    #     # Загружаем модель
    #     model = SentenceTransformer("all-MiniLM-L6-v2")

    #     # Читаем текст
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         text = f.read()

    #     # Нарезаем текст по 500 символов
    #     chunk_size = 500
    #     chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    #     # Получаем эмбеддинги
    #     embeddings = model.encode(chunks)

    #     # Сохраняем векторы + куски
    #     data = [{"text": chunk, "embedding": emb.tolist()} for chunk, emb in zip(chunks, embeddings)]
        
    #     # Формируем путь к .json-файлу
    #     base_name = os.path.splitext(file_path)[0]  # без расширения
    #     json_path = base_name + ".json"

    #     with open(json_path, "w", encoding="utf-8") as f:
    #         json.dump(data, f, ensure_ascii=False, indent=2)

    #     print(f"Сохранено {len(data)} векторных фрагментов в embeddings.json")
    #     return json_path
    
    
    async def get_unique_filenames():
        folder_path="files"
        unique_names = set()

        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                name_wo_ext = os.path.splitext(filename)[0]
                unique_names.add(name_wo_ext)
        print(sorted(unique_names))
        return sorted(unique_names)
    

    async def delete_all_versions_by_name(doc_name: str) -> int:
        folder_path="files"
        deleted = False
        for filename in os.listdir(folder_path):
            base_name, _ = os.path.splitext(filename)
            if base_name == doc_name:
                file_path = os.path.join(folder_path, filename)
                try:
                    os.remove(file_path)
                    deleted = True
                    print(f"[✔] Удалён файл: {file_path}")
                except Exception as e:
                    print(f"[!] Ошибка при удалении {file_path}: {e}")
        return deleted