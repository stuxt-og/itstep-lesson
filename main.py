import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

RESPONSE_SCHEMA = {
    "name": "bill_gates_post",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Тема згенерованого допису."
            },
            "text": {
                "type": "string",
                "description": "Згенерований текст допису у стилі Білла Гейтса."
            },
            "tone": {
                "type": "string",
                "description": "Загальний тон допису (наприклад: оптимістичний, стурбований, надихаючий)."
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Доречні хештеги без символу #."
            },
            "mentions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Доречні згадки без символу @."
            },
            "word_count": {
                "type": "integer",
                "description": "Кількість слів у згенерованому тексті."
            }
        },
        "required": ["topic", "text", "tone", "hashtags", "mentions", "word_count"],
        "additionalProperties": False
    }
}


def load_posts(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Файл {path} не знайдено.")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    raw_posts = data.get("posts", [])
    posts = []
    for entry in raw_posts:
        if not isinstance(entry, dict):
            continue
        text = entry.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        posts.append({
            "id": entry.get("id"),
            "text": text.strip(),
        })

    if not posts:
        raise ValueError(f"У файлі {path} немає жодного поста.")

    return posts


def mimic_style(posts: list[dict], user_prompt: str) -> dict:
    client = OpenAI()

    samples = "\n---\n".join(p["text"] for p in posts)

    system_prompt = (
        "Ти — імітатор, створений для відтворення стилю письма Білла Гейтса. "
        "Тобі надано набір зразків дописів, написаних Біллом Гейтсом. "
        "Твоє завдання — імітувати його стиль письма, приділяючи пильну увагу "
        "лексичному багатству та різноманітності, структурі речень, пунктуації, "
        "виразам та ідіомам, а також загальному тону, емоційному забарвленню та настрою. "
        "Переконайся, що згенерований текст неможливо відрізнити від наданих зразків.\n\n"
        f"Зразки дописів:\n{samples}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        response_format={
            "type": "json_schema",
            "json_schema": RESPONSE_SCHEMA,
        },
    )

    content = response.choices[0].message.content
    return json.loads(content)


def main():
    POSTS_FILE = Path("posts.json")

    print(f"Читаємо пости з {POSTS_FILE}...")
    try:
        posts = load_posts(POSTS_FILE)
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return

    print(f"Завантажено {len(posts)} постів.\n")

    while True:
        prompt = input("Промпт (Enter для прикладу): ").strip()
        if not prompt:
            prompt = "Напиши новий пост у стилі Білла Гейтса про важливість штучного інтелекту в освіті."
        elif prompt == "стоп":
            break

        try:
            result = mimic_style(posts, prompt)
        except Exception as e:
            print(f"Помилка OpenAI API: {e}")
            return

        print("Згенерований JSON:\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()


if __name__ == "__main__":
    main()