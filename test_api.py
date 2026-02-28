from openai import OpenAI

openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    base_url=openai_api_base,
    api_key=openai_api_key,
)

MODEL_PATH = 'hunyuan-a13b'

temperature = 0.05
top_p = 0.1
repetition_penalty = 1.05
max_tokens = 128


completion = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {'type': 'text', 'text': 'hello'},
        ]},
    ],
    temperature=temperature,  # Temperature for text generation
    top_p=top_p,
    max_tokens=max_tokens,
    extra_body={
        'repetition_penalty': repetition_penalty,
    }
)

print(completion.choices[0].message)
