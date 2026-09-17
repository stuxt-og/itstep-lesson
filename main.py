import json
import re
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
            "score": {"type": "integer", "description": "Оцінка від 0 до 100."},
            "issues": {"type": "array", "items": {"type": "string"}, "description": "Список конкретних проблем."},
            "recommendations": {"type": "array", "items": {"type": "string"}, "description": "Список порад."},
            "analyzed_source": {"type": "string", "description": "Що саме було проаналізовано (файл/запис)."}
        },
        "required": ["score", "issues", "recommendations", "analyzed_source"],
        "additionalProperties": False
    }
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_posts",
            "description": (
                "Шукає у posts.json пости за ключовими словами. "
                "Використовуй, коли користувач просить зробити текст на певну тему "
                "і хоче бачити, як Білл Гейтс писав про це раніше."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Ключові слова для пошуку."},
                    "limit": {"type": "integer", "description": "Максимальна кількість результатів (1-10)."}
                },
                "required": ["query", "limit"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_post",
            "description": (
                "Повертає один конкретний пост з posts.json за його id. "
                "Використовуй, коли користувач каже «зроби схожий на пост №5» "
                "або явно посилається на номер поста."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Ідентифікатор поста."}
                },
                "required": ["id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_generated_files",
            "description": (
                "Повертає список усіх збережених файлів у теці outputs/ "
                "із зазначенням часу останньої зміни. Використовуй, коли "
                "користувач каже «оціни останній файл» або «покажи, що є»."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_generated_file",
            "description": (
                "Читає вміст конкретного файлу з outputs/ за його назвою. "
                "Повертає всі записи (генерації), які збережені в цьому файлі."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Назва файлу, наприклад 'generated.json'."}
                },
                "required": ["name"],
                "additionalProperties": False
            }
        }
    }
]

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

def search_posts(posts: list[dict], query: str, limit: int = 3) -> dict:
    limit = max(1, min(limit, 10))
    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
    if not words:
        return {"results": posts[:limit]}
    scored = []
    for p in posts:
        text_lower = p["text"].lower()
        score = sum(text_lower.count(w) for w in words)
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    results = [{"id": p["id"], "text": p["text"]} for _, p in scored[:limit]]
    if not results:
        results = [{"id": p["id"], "text": p["text"]} for p in posts[:limit]]
    return {"query": query, "count": len(results), "results": results}


def get_post(posts: list[dict], post_id: int) -> dict:
    for p in posts:
        if p["id"] == post_id:
            return {"id": p["id"], "text": p["text"]}
    return {"error": f"Пост з id={post_id} не знайдено."}

def list_generated_files() -> dict:
    OUTPUT_DIR.mkdir(exist_ok=True)
    files = list(OUTPUT_DIR.glob("*.json"))
    if not files:
        return {"files": [], "note": "Тека outputs/ порожня."}
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return {
        "files": [
            {
                "name": f.name,
                "size_bytes": f.stat().st_size,
                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f.stat().st_mtime)),
                "is_latest": i == 0
            }
            for i, f in enumerate(files)
        ],
        "note": "Файли відсортовані від найновішого до найстарішого."
    }

def read_generated_file(name: str) -> dict:
    path = OUTPUT_DIR / name
    if not path.exists():
        return {"error": f"Файл {name} не знайдено."}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"Невалідний JSON: {e}"}
    return {"name": name, "content": data}

def execute_tool(name: str, args: dict, posts: list[dict]) -> str:
    try:
        if name == "search_posts":
            result = search_posts(posts, args["query"], int(args.get("limit", 3)))
        elif name == "get_post":
            result = get_post(posts, int(args["id"]))
        elif name == "list_generated_files":
            result = list_generated_files()
        elif name == "read_generated_file":
            result = read_generated_file(args["name"])
        else:
            result = {"error": f"Невідомий тул: {name}"}
    except Exception as e:
        result = {"error": f"Помилка виконання {name}: {e}"}
    return json.dumps(result, ensure_ascii=False)


def build_imitation_prompt(posts: list[dict]) -> str:
    samples = "\n---\n".join(p["text"] for p in posts)
    return (
        "Ти — імітатор, створений для відтворення стилю письма Білла Гейтса. "
        "Тобі надано набір зразків дописів, написаних Біллом Гейтсом. "
        "Твоє завдання — імітувати його стиль письма, приділяючи пильну увагу "
        "лексичному багатству та різноманітності, структурі речень, пунктуації, "
        "виразам та ідіомам, а також загальному тону, емоційному забарвленню та настрою.\n\n"
        "У тебе є тули: search_posts(query, limit) для пошуку серед оригінальних постів "
        "і get_post(id) для отримання конкретного поста. Використовуй їх, коли користувач "
        "просить зробити текст схожим на конкретний пост або на певну тему.\n\n"
        f"Зразки дописів:\n{samples}"
    )

def build_judge_prompt(posts: list[dict]) -> str:
    samples = "\n---\n".join(p["text"] for p in posts)
    return (
        "Ти — суддя-експерт, який оцінює, наскільки згенерований текст імітує стиль Білла Гейтса. "
        "Проаналізуй лексику, структуру речень, пунктуацію, тон, емоційне забарвлення, "
        "ідіоматичні вирази та загальну відповідність стилю.\n\n"
        "У тебе є тули:\n"
        "- list_generated_files() — список збережених файлів у outputs/ (найновіший перший).\n"
        "- read_generated_file(name) — читає вміст файлу, повертає всі записи.\n"
        "- search_posts(query, limit) — пошук серед оригінальних постів Білла Гейтса.\n"
        "- get_post(id) — конкретний оригінальний пост.\n\n"
        "Якщо користувач каже «оціни останній файл» — виклич list_generated_files(), "
        "візьми перший (is_latest=true), потім read_generated_file() і оціни останній запис. "
        "Якщо згадує конкретне ім'я чи номер — використай відповідний тул.\n\n"
        "Поверни:\n"
        "- score: ціла оцінка від 0 до 100.\n"
        "- issues: список конкретних проблем.\n"
        "- recommendations: список конкретних порад.\n"
        "- analyzed_source: короткий опис того, що саме було проаналізовано.\n\n"
        f"Оригінальні зразки:\n{samples}"
    )

def call_api_with_tools(client: OpenAI, system_prompt: str, messages: list[dict],
                        schema: dict, posts: list[dict],
                        max_iterations: int = 8) -> tuple[dict, dict, float, list[str]]:
    start = time.perf_counter()
    total_prompt = 0
    total_completion = 0
    tool_log = []

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=1500,
            response_format={"type": "json_schema", "json_schema": schema},
            tools=TOOLS,
        )

        total_prompt += response.usage.prompt_tokens
        total_completion += response.usage.completion_tokens

        choice = response.choices[0]
        msg = choice.message

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } for tc in msg.tool_calls
                ]
            })
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}
                tool_log.append(f"{tc.function.name}({json.dumps(args, ensure_ascii=False)})")
                result = execute_tool(tc.function.name, args, posts)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            continue

        if choice.finish_reason == "length":
            raise RuntimeError(f"Відповідь обірвана (max_tokens). Фрагмент:\n{msg.content}")

        try:
            result = json.loads(msg.content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Невалідний JSON: {e}\n{msg.content}") from e

        elapsed = time.perf_counter() - start
        usage = {
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
        }
        return result, usage, elapsed, tool_log

    raise RuntimeError("Перевищено ліміт ітерацій виклику тулів.")

def print_stats(usage: dict, cost: dict, elapsed: float, tool_log: list[str]):
    print("\n--- Статистика ---")
    print(f"Час:            {elapsed:.2f} с")
    print(f"Вхідні токени:  {usage['prompt_tokens']}")
    print(f"Вихідні токени: {usage['completion_tokens']}")
    print(f"Вартість входу:  ${cost['input_cost']:.6f}")
    print(f"Вартість виходу: ${cost['output_cost']:.6f}")
    print(f"Вартість разом:  ${cost['total_cost']:.6f}")
    if tool_log:
        print("Викликані тули:")
        for entry in tool_log:
            print(f"  → {entry}")

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
    name = input("Назва файлу (Enter — generated.json): ").strip() or "generated.json"
    if not name.endswith(".json"):
        name += ".json"
    output_path = OUTPUT_DIR / name

    system_prompt = build_imitation_prompt(posts)

    prompt = input("Промпт (Enter для прикладу): ").strip() or \
        "Напиши новий пост у стилі Білла Гейтса про важливість штучного інтелекту в освіті."

    messages = [{"role": "user", "content": prompt}]

    total = {"prompt": 0, "completion": 0, "cost": 0.0, "time": 0.0}

    try:
        result, usage, elapsed, tool_log = call_api_with_tools(
            client, system_prompt, messages, GENERATION_SCHEMA, posts
        )
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
    print_stats(usage, cost, elapsed, tool_log)

    while True:
        followup = input("\nДодатковий запит (Enter — завершити): ").strip()
        if not followup:
            break
        messages.append({"role": "user", "content": followup})
        try:
            result, usage, elapsed, tool_log = call_api_with_tools(
                client, system_prompt, messages, GENERATION_SCHEMA, posts
            )
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
        print_stats(usage, cost, elapsed, tool_log)

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

def analyze_flow(client: OpenAI, posts: list[dict]):
    query = input(
        "Запит (напр. 'оціни останній файл', 'проаналізуй generated.json'): "
    ).strip() or "оціни останній згенерований файл"

    system_prompt = build_judge_prompt(posts)
    messages = [{"role": "user", "content": query}]

    try:
        result, usage, elapsed, tool_log = call_api_with_tools(
            client, system_prompt, messages, JUDGE_SCHEMA, posts
        )
    except Exception as e:
        print(f"Помилка OpenAI API: {e}")
        return

    cost = calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])

    print(f"\n=== Оцінка судді ===\n")
    print(f"Джерело: {result['analyzed_source']}")
    print(f"Оцінка:  {result['score']}/100\n")
    print("Проблеми:")
    for issue in result["issues"]:
        print(f"  • {issue}")
    print("\nРекомендації:")
    for rec in result["recommendations"]:
        print(f"  • {rec}")

    print_stats(usage, cost, elapsed, tool_log)


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
