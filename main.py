import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # OPENAI_API_KEY from env variables

def load_posts(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Файл {path} не знайдено.")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("posts", [])
    posts = [p.strip() for p in posts if isinstance(p, str) and p.strip()]

    if not posts:
        raise ValueError(f"У файлі {path} немає жодного поста.")

    return posts


def mimic_style(posts: list[str], user_prompt: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    samples = "\n---\n".join(posts)

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
        max_tokens=300
    )

    return response.choices[0].message.content


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

        print("Згенерований текст:\n")
        print(result)


if __name__ == "__main__":
    main()
