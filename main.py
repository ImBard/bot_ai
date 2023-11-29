import telebot
import requests
import os
import re
from dotenv import load_dotenv
load_dotenv()

telebot_key = os.getenv("TELEBOT_KEY")
url = os.getenv("API_URL")
secret_key = os.getenv("CHATCSV_KEY")

messages = [
  {"role": "system", "content": "You are a wizard who just provides information and image links to the user in addition to any CSV data provided to you. you should not provide any code in python or any other programming language"},
]

csv_link = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
csv_links = {}

def formatText(texto):
    texto_modificado = re.sub(r'\[|\]|\(|\)', '', texto)
    texto_modificado = re.sub(r'(\w)(https)', r'\1 \2', texto_modificado)

    for c in range(0, len(texto_modificado) - 5):
      if texto_modificado[c:c+5] == "https":
        print(texto_modificado[c:c+5])    
    
    return texto_modificado

def verificar(texto):
    padrao = r'\[|\]|\(|\)'
    if re.search(padrao, texto):
        return formatText(texto)
    else:
        return texto

def query(message):
  headers = {
      'accept': 'text/event-stream',
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {secret_key}',
  }

  messages.append({
    "role": "user",
    "content": f"{message}"
  })

  print(csv_link)

  data = {
      "model": "gpt-3.5-turbo-16k-0613",
      "messages": messages,
      "files": [
          csv_link
      ]
  }
  
  response = requests.post(url, json=data, headers=headers)
  messages.append({
    "user": "assistant",
    "content": response.text,
    })
  return response

bot = telebot.TeleBot(telebot_key)

@bot.message_handler(commands=['help'])
def helping_user(message):
  help = '''
  This bot utilizes AI to provide information about any CSV or a default CSV related to the Titanic.

- How to use:
    You can ask anything about the Titanic, and I'll provide you with images and information.
    You can also send me your CSV file, and I'll provide you with the data about then.

- How to send my CSV:
    First, you need to host your CSV online.
    Later, you can send the command "/csv" in the chat, and I will request the link.
'''
  bot.reply_to(message, help)

@bot.message_handler(commands=['csv'])
def request_csv_link(message):
    # Pergunta ao usuário qual link CSV ele quer usar
    msg = bot.reply_to(message, "Por favor, forneça o link do CSV que você deseja usar.")
    # Adiciona o ID do usuário à lista de espera para a resposta do link CSV
    bot.register_next_step_handler(msg, process_csv_link)

def process_csv_link(message):
    global csv_link
    # Obtém o link CSV da mensagem do usuário
    get_csv_link = message.text
    # Armazena o link CSV associado ao ID do usuário
    csv_links[message.from_user.id] = get_csv_link
    # Pode realizar outras ações com o link CSV, se necessário
    csv_link = get_csv_link
    print(get_csv_link)

    bot.reply_to(message, f"Link CSV recebido com sucesso: {csv_link}")

@bot.message_handler()
def send_welcome(message):
  print(message.json["text"])
  
  response = query(message.json['text'])

  responseText = verificar(response.text)
  
  if response.status_code == 200:
    bot.reply_to(message, responseText)

bot.infinity_polling()