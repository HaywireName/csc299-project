
from openai import OpenAI

try:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Respond with OK"}]
    )
    print("✓ API Working:", response.choices[0].message.content)
except Exception as e:
    print("✗ Error:", e)