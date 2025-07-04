!pip install google-genai requests

from google import genai
from google.genai import types
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

gemini_api = 'AIzaSyBjCMFPAv1QX5ewcb0m08Pjh4Mdn6MV9i8'
sora_api = 'sk-bCREbtCgwOgFPHxdFd4c7a9910A140438507D1C51401827c'
sora_url = "https://api.laozhang.ai/v1/chat/completions"

def get_best_prompt(user_input):
    client = genai.Client(api_key=gemini_api)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=(
            "Напиши очень подробный промпт для Sora, кроме промпта не должно быть лишних слов."
            "Задача нарисовать картинку в лучшем виде, на придумывать много лишнего,"
            "главная задача сохранить исходную идею, ниже запрос пользователя, ответ на англиском языке:\n"
            f"{user_input}"
        )
    )
    print(response.text)
    return response.text

def get_image_from_kitai_sora(best_prompt):
    headers = {
        "Authorization": f"Bearer {sora_api}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sora-image",
        "stream": False,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": best_prompt}
        ],
    }
    resp = requests.post(sora_url, headers=headers, json=payload)
    print(resp)
    return get_image_from_resp(resp.json())

def get_image_from_resp(data):
    content = data["choices"][0]["message"]["content"]
    return re.findall(r"\((https?://[^\s)]+)\)", content)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    user_input = data.get('text')

    if not user_input:
        return jsonify({"error": "Nety texta"}), 400

    prompt = get_best_prompt(user_input)
    urls = get_image_from_kitai_sora(prompt)
    img_url_s_best_prompt = urls[0] if urls else ""

    return jsonify({"image_url": img_url_s_best_prompt})

if __name__ == '__main__':
    app.run()
