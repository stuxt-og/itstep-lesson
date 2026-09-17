import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

INPUT_PRICE_PER_1M = 0.15
OUTPUT_PRICE_PER_1M = 0.60

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


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> dict:
    input_cost = prompt_tokens * INPUT_PRICE_PER_1M / 1_000_000
    output_cost = completion_tokens * OUTPUT_PRICE_PER_1M / 1_000_000
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
    }


def mimic_style(posts: list[dict], user_prompt: str) -> tuple[dict, dict]:
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
    result = json.loads(content)

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return result, usage


def format_cost(cost: float) -> str:
    return f"${cost:.6f}"


def main():
    POSTS_FILE = Path("posts.json")

    print(f"Читаємо пости з {POSTS_FILE}...")
    try:
        posts = load_posts(POSTS_FILE)
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return

    print(f"Завантажено {len(posts)} постів.\n")

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0.0

    while True:
        prompt = input("Промпт (Enter для прикладу): ").strip()
        if not prompt:
            prompt = "Напиши новий пост у стилі Білла Гейтса про важливість штучного інтелекту в освіті."
        elif prompt == "стоп":
            break

        try:
            result, usage = mimic_style(posts, prompt)
        except Exception as e:
            print(f"Помилка OpenAI API: {e}")
            return

        cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])

        total_prompt_tokens += usage["prompt_tokens"]
        total_completion_tokens += usage["completion_tokens"]
        total_cost += cost["total_cost"]

        print("Згенерований JSON:\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        print("\nСтатистика запиту:")
        print(f"Вхідні токени:  {usage['prompt_tokens']}")
        print(f"Вихідні токени: {usage['completion_tokens']}")
        print(f"Всього токенів: {usage['total_tokens']}")
        print(f"Вартість входу:  {format_cost(cost['input_cost'])}")
        print(f"Вартість виходу: {format_cost(cost['output_cost'])}")
        print(f"Вартість разом:  {format_cost(cost['total_cost'])}")
        print()

    if total_prompt_tokens > 0:
        print("=" * 40)
        print("ЗАГАЛЬНА СТАТИСТИКА СЕСІЇ")
        print("=" * 40)
        print(f"Вхідні токени:  {total_prompt_tokens}")
        print(f"Вихідні токени: {total_completion_tokens}")
        print(f"Всього токенів: {total_prompt_tokens + total_completion_tokens}")
        print(f"Загальна вартість: ${total_cost:.6f}")
        print()


if __name__ == "__main__":
    main()
