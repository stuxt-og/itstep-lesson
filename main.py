import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

INPUT_PRICE_PER_1M = 0.15
OUTPUT_PRICE_PER_1M = 0.60
OUTPUT_FILE = Path("generated.json")
POSTS_FILE = Path("posts.json")

RESPONSE_SCHEMA = {
    "name": "bill_gates_post",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Тема згенерованого допису."},
            "text": {"type": "string", "description": "Згенерований текст допису у стилі Білла Гейтса."},
            "tone": {"type": "string", "description": "Загальний тон допису."},
            "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Доречні хештеги без #."},
            "mentions": {"type": "array", "items": {"type": "string"}, "description": "Доречні згадки без @."},
            "word_count": {"type": "integer", "description": "Кількість слів у тексті."}
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
    posts = []
    for entry in data.get("posts", []):
        if isinstance(entry, dict) and isinstance(entry.get("text"), str) and entry["text"].strip():
            posts.append({"id": entry.get("id"), "text": entry["text"].strip()})
    if not posts:
        raise ValueError(f"У файлі {path} немає жодного поста.")
    return posts

def calculate_cost(prompt_tokens: int, completion_tokens: int) -> dict:
    input_cost = prompt_tokens * INPUT_PRICE_PER_1M / 1_000_000
    output_cost = completion_tokens * OUTPUT_PRICE_PER_1M / 1_000_000
    return {"input_cost": input_cost, "output_cost": output_cost, "total_cost": input_cost + output_cost}

def build_system_prompt(posts: list[dict]) -> str:
    samples = "\n---\n".join(p["text"] for p in posts)
    return (
        "Ти — імітатор, створений для відтворення стилю письма Білла Гейтса. "
        "Тобі надано набір зразків дописів, написаних Біллом Гейтсом. "
        "Твоє завдання — імітувати його стиль письма, приділяючи пильну увагу "
        "лексичному багатству та різноманітності, структурі речень, пунктуації, "
        "виразам та ідіомам, а також загальному тону, емоційному забарвленню та настрою. "
        "Переконайся, що згенерований текст неможливо відрізнити від наданих зразків.\n\n"
        f"Зразки дописів:\n{samples}"
    )

def call_api(client: OpenAI, system_prompt: str, messages: list[dict]) -> tuple[dict, dict, float]:
    start = time.perf_counter()
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        max_tokens=1500,
        response_format={"type": "json_schema", "json_schema": RESPONSE_SCHEMA},
    )
    elapsed = time.perf_counter() - start

    choice = response.choices[0]
    content = choice.message.content
    finish_reason = choice.finish_reason

    if finish_reason == "length":
        raise RuntimeError(
            "Відповідь обірвана: досягнуто ліміт max_tokens. "
            "Збільште max_tokens або скоротіть історію діалогу.\n"
            f"Отриманий фрагмент:\n{content}"
        )

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Не вдалося розпарсити JSON: {e}\n"
            f"finish_reason={finish_reason}\n"
            f"Сирий вміст:\n{content}"
        ) from e

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return result, usage, elapsed

def save_output(entry: dict):
    history = []
    if OUTPUT_FILE.exists():
        try:
            history = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = [history]
        except json.JSONDecodeError:
            history = []
    history.append(entry)
    OUTPUT_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def print_stats(usage: dict, cost: dict, elapsed: float):
    print("\n--- Статистика ---")
    print(f"Час генерації:  {elapsed:.2f} с")
    print(f"Вхідні токени:  {usage['prompt_tokens']}")
    print(f"Вихідні токени: {usage['completion_tokens']}")
    print(f"Вартість входу:  ${cost['input_cost']:.6f}")
    print(f"Вартість виходу: ${cost['output_cost']:.6f}")
    print(f"Вартість разом:  ${cost['total_cost']:.6f}")

def print_result(result: dict):
    print("\nЗгенерований JSON:\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    print(f"Читаємо пости з {POSTS_FILE}...")
    try:
        posts = load_posts(POSTS_FILE)
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return

    print(f"Завантажено {len(posts)} постів.\n")

    client = OpenAI()
    system_prompt = build_system_prompt(posts)

    total = {"prompt": 0, "completion": 0, "cost": 0.0, "time": 0.0}

    prompt = input("Промпт (Enter для прикладу): ").strip() or \
        "Напиши новий пост у стилі Білла Гейтса про важливість штучного інтелекту в освіті."

    messages = [{"role": "user", "content": prompt}]

    try:
        result, usage, elapsed = call_api(client, system_prompt, messages)
    except Exception as e:
        print(f"Помилка OpenAI API: {e}")
        return

    cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])
    total["prompt"] += usage["prompt_tokens"]
    total["completion"] += usage["completion_tokens"]
    total["cost"] += cost["total_cost"]
    total["time"] += elapsed

    print_result(result)
    print_stats(usage, cost, elapsed)

    messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})

    while True:
        followup = input("\nДодатковий запит (Enter — завершити, 'стоп' — вийти): ").strip()
        if not followup or followup.lower() in ("стоп", "stop", "exit", "q"):
            break

        messages.append({"role": "user", "content": followup})

        try:
            result, usage, elapsed = call_api(client, system_prompt, messages)
        except Exception as e:
            print(f"Помилка OpenAI API: {e}")
            break

        cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])
        total["prompt"] += usage["prompt_tokens"]
        total["completion"] += usage["completion_tokens"]
        total["cost"] += cost["total_cost"]
        total["time"] += elapsed

        print_result(result)
        print_stats(usage, cost, elapsed)

        messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})

    save_output({
        "prompt": prompt,
        "final_result": result,
        "stats": {
            "prompt_tokens": total["prompt"],
            "completion_tokens": total["completion"],
            "total_tokens": total["prompt"] + total["completion"],
            "total_cost": total["cost"],
            "total_time": total["time"],
        }
    })

    print("\n" + "=" * 40)
    print("ЗАГАЛЬНА СТАТИСТИКА СЕСІЇ")
    print("=" * 40)
    print(f"Вхідні токени:   {total['prompt']}")
    print(f"Вихідні токени:  {total['completion']}")
    print(f"Всього токенів:  {total['prompt'] + total['completion']}")
    print(f"Загальний час:   {total['time']:.2f} с")
    print(f"Загальна вартість: ${total['cost']:.6f}")
    print(f"Збережено у:     {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
