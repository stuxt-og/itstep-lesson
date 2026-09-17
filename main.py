import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

INPUT_PRICE_PER_1M = 0.15
OUTPUT_PRICE_PER_1M = 0.60
MODEL = "gpt-4o-mini-2024-07-18"
POSTS_FILE = Path("posts.json")
OUTPUT_DIR = Path("outputs")

GENERATION_SCHEMA = {
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

JUDGE_SCHEMA = {
    "name": "judge_evaluation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "integer",
                "description": "Оцінка від 0 до 100, де 100 — неможливо відрізнити від оригіналу."
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Список конкретних проблем у тексті."
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Список конкретних порад, як покращити текст."
            }
        },
        "required": ["score", "issues", "recommendations"],
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

def build_imitation_prompt(posts: list[dict]) -> str:
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

def build_judge_prompt(posts: list[dict]) -> str:
    samples = "\n---\n".join(p["text"] for p in posts)
    return (
        "Ти — суддя-експерт, який оцінює, наскільки згенерований текст імітує стиль Білла Гейтса. "
        "Тобі надані оригінальні зразки його дописів і текст, який потрібно оцінити. "
        "Проаналізуй лексику, структуру речень, пунктуацію, тон, емоційне забарвлення, "
        "ідіоматичні вирази та загальну відповідність стилю.\n\n"
        "Поверни:\n"
        "- score: ціла оцінка від 0 до 100, де 100 — неможливо відрізнити від оригіналу.\n"
        "- issues: список конкретних проблем (чого не вистачає, що виглядає чужорідно).\n"
        "- recommendations: список конкретних, дієвих порад для покращення.\n\n"
        "Будь вимогливим і конкретним. Уникай загальних фраз.\n\n"
        f"Оригінальні зразки:\n{samples}"
    )

def call_api(client: OpenAI, system_prompt: str, messages: list[dict], schema: dict) -> tuple[dict, dict, float]:
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + messages,
        max_tokens=1500,
        response_format={"type": "json_schema", "json_schema": schema},
    )
    elapsed = time.perf_counter() - start

    choice = response.choices[0]
    content = choice.message.content

    if choice.finish_reason == "length":
        raise RuntimeError(f"Відповідь обірвана (max_tokens). Фрагмент:\n{content}")

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Невалідний JSON: {e}\n{content}") from e

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return result, usage, elapsed

def print_stats(usage: dict, cost: dict, elapsed: float):
    print("\n--- Статистика ---")
    print(f"Час:            {elapsed:.2f} с")
    print(f"Вхідні токени:  {usage['prompt_tokens']}")
    print(f"Вихідні токени: {usage['completion_tokens']}")
    print(f"Вартість входу:  ${cost['input_cost']:.6f}")
    print(f"Вартість виходу: ${cost['output_cost']:.6f}")
    print(f"Вартість разом:  ${cost['total_cost']:.6f}")

def save_output(path: Path, entry: dict):
    history = []
    if path.exists():
        try:
            history = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = [history]
        except json.JSONDecodeError:
            history = []
    history.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def generate_flow(client: OpenAI, posts: list[dict]):
    name = input("Назва файлу (Enter — generated.json): ").strip()
    if not name:
        name = "generated.json"
    if not name.endswith(".json"):
        name += ".json"
    output_path = OUTPUT_DIR / name

    system_prompt = build_imitation_prompt(posts)

    prompt = input("Промпт (Enter для прикладу): ").strip() or \
        "Напиши новий пост у стилі Білла Гейтса про важливість штучного інтелекту в освіті."

    messages = [{"role": "user", "content": prompt}]

    total = {"prompt": 0, "completion": 0, "cost": 0.0, "time": 0.0}

    try:
        result, usage, elapsed = call_api(client, system_prompt, messages, GENERATION_SCHEMA)
    except Exception as e:
        print(f"Помилка OpenAI API: {e}")
        return

    cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])
    total["prompt"] += usage["prompt_tokens"]
    total["completion"] += usage["completion_tokens"]
    total["cost"] += cost["total_cost"]
    total["time"] += elapsed

    print("\nЗгенерований JSON:\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print_stats(usage, cost, elapsed)

    messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})

    while True:
        followup = input("\nДодатковий запит (Enter — завершити): ").strip()
        if not followup:
            break
        messages.append({"role": "user", "content": followup})
        try:
            result, usage, elapsed = call_api(client, system_prompt, messages, GENERATION_SCHEMA)
        except Exception as e:
            print(f"Помилка OpenAI API: {e}")
            break

        cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])
        total["prompt"] += usage["prompt_tokens"]
        total["completion"] += usage["completion_tokens"]
        total["cost"] += cost["total_cost"]
        total["time"] += elapsed

        print("\nЗгенерований JSON:\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print_stats(usage, cost, elapsed)

        messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})

    save_output(output_path, {
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

    print(f"\n💾 Збережено у {output_path}")
    print(f"Загальна вартість сесії: ${total['cost']:.6f}, час: {total['time']:.2f} с")

def list_output_files() -> list[Path]:
    OUTPUT_DIR.mkdir(exist_ok=True)
    return sorted(OUTPUT_DIR.glob("*.json"))

def analyze_flow(client: OpenAI, posts: list[dict]):
    files = list_output_files()
    if not files:
        print("Немає збережених файлів у теці outputs/.")
        return

    print("Доступні файли:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.name}")
    raw = input("Номер файлу: ").strip()
    try:
        path = files[int(raw) - 1]
    except (ValueError, IndexError):
        print("Невірний вибір.")
        return

    try:
        history = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Не вдалося прочитати файл: {e}")
        return
    if not isinstance(history, list):
        history = [history]

    print(f"\nЗаписи у {path.name}:")
    for i, entry in enumerate(history, 1):
        p = entry.get("prompt", "")
        text = entry.get("final_result", {}).get("text", "")
        preview = text[:70] + ("..." if len(text) > 70 else "")
        print(f"  {i}. [{p[:40]}] {preview}")

    raw = input("Номер запису: ").strip()
    try:
        entry = history[int(raw) - 1]
    except (ValueError, IndexError):
        print("Невірний вибір.")
        return

    text = entry.get("final_result", {}).get("text", "").strip()
    if not text:
        print("У записі немає тексту для оцінки.")
        return

    system_prompt = build_judge_prompt(posts)
    messages = [{"role": "user", "content": f"Оціни цей текст:\n\n{text}"}]

    try:
        result, usage, elapsed = call_api(client, system_prompt, messages, JUDGE_SCHEMA)
    except Exception as e:
        print(f"Помилка OpenAI API: {e}")
        return

    cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])

    print("\n=== Оцінка судді ===\n")
    print(f"Оцінка: {result['score']}/100\n")
    print("Проблеми:")
    for issue in result["issues"]:
        print(f"  • {issue}")
    print("\nРекомендації:")
    for rec in result["recommendations"]:
        print(f"  • {rec}")

    print_stats(usage, cost, elapsed)

def menu() -> str:
    print("\n=== Меню ===")
    print("1. Згенерувати новий текст")
    print("2. Проаналізувати збережений файл (суддя)")
    print("0. Вихід")
    return input("Оберіть дію: ").strip()

def main():
    print(f"Читаємо пости з {POSTS_FILE}...")
    try:
        posts = load_posts(POSTS_FILE)
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return
    print(f"Завантажено {len(posts)} постів.")

    client = OpenAI()

    while True:
        choice = menu()
        if choice == "1":
            generate_flow(client, posts)
        elif choice == "2":
            analyze_flow(client, posts)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.")

if __name__ == "__main__":
    main()
