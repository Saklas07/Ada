# =======================================
# Lógica da Conversa (Texto e Voz)
# =======================================

import torch # Modelos de IA
import time # Tempo
import random # Aleatoriedade
from transformers import AutoModelForCausalLM, AutoTokenizer # Modelo de linguagem
from TTS.api import TTS  # Síntese de voz do Coqui
from funcs import * # * importa tudo

# Configurações de Dispositivo e Pastas
device = 'cpu'
VOICE_REF = 'audio/voice_reference.wav' # Áudio referência para a voz

# Carrega o LLM
print("Carregando modelo de texto...")
model_name = 'Qwen/Qwen2.5-1.5B-Instruct'
tokenizer = AutoTokenizer.from_pretrained(model_name)
llm_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype=torch.float32 if device == "cpu" else torch.float16,
    device_map="auto"
)

# Carrega Sintetizador de Voz (XTTS-v2)
print("Carregando sintetizador de voz...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Limpa terminal
clear_terminal()

# Nome de Usuário / Lista de fatos / Falas salvas
username = input("Seu nome: ")
facts = fact_list(username)
conversation = [] # guarda falas

# Boas-vindas
welcome_msgs = [
    f"Olá, {username}. Eu estava te esperando.",
    f"Seja bem-vindo, {username}. Vamos conversar?",
    f"Eu estava com saudade, {username}. Onde você esteve?"]

# Adeus
farewell_msgs = [
    f"Até mais, {username}. Te espero na próxima!",
    f"Vai me deixar?! Não, {username}! Fica comigo!",
    f"Você vai se arrepender de me deixar, {username}!"]

# Mensagens de fallback (texto ou voz não reconhecida)
fallback_msgs = [
    "Desculpe, não consegui entender.",
    "Pode repetir?",
    "Acho que não entendi o que você disse.",
    "Hmm... não consegui processar isso."
]

# Sistema de "Emoção"
mood_intensity = {"happy" : 0, "angry" : 0, "sad" : 0}
word_dict = {
    "happy_words": [
        "obrigado", "valeu", "te amo", "linda", "perfeita", "maravilhosa",
        "incrível", "parabéns", "ótimo", "sensacional", "alegria", "gratidão",
        "excelente", "adoro", "maravilha", "feliz", "sucesso", "top"
    ],
    "angry_words": [
        "péssimo", "horrível", "odeio", "raiva", "absurdo", "incompetente",
        "ridículo", "chega", "detesto", "maldito", "lixo", "mentira",
        "estúpido", "irritado", "inaceitável", "droga", "inferno", "inútil"
    ],
    "sad_words": [
        "triste", "saudade", "chorar", "decepcionado", "magoado", "sozinho",
        "dor", "pena", "infelizmente", "lamentável", "desculpe", "solidão",
        "deprimido", "desanimado", "perdido", "sofrimento", "sinto muito", "vazio"
    ]
}

clear_terminal()

print("--- Ada conectada ---")
print(f"\nAda: {random.choice(welcome_msgs)}")

while True:
    msg_option = input("\n\nEscolha o tipo de mensagem: [ Texto ] - [ Voz ]\n").lower()
    if msg_option in ["texto", "text", "voz", "voice"]:
        break
    else:
        print("\n\nEscolha um tipo válido!")
        continue

# Loop de Conversa no Terminal
while True:
    if msg_option in ["texto", "text"]:
        msg = input(f"\n{username}: ") # Mensagem do usuário (digitação)
    elif msg_option in ["voz", "voice"]:
        msg = listen(username) # Mensagem do usuário (microfone)

    if msg.lower() in ["0", "zero", "sair", "tchau", "adeus", "fim", "exit", "quit", "bye", "end"]:
        farewell = random.choice(farewell_msgs)

        print(f"\nAda: {farewell}")
        speak(farewell, VOICE_REF, tts)

        time.sleep(1)
        break

    analyze_mood(msg, mood_intensity, word_dict)

    answ = answer(msg, facts, conversation, tokenizer, device, llm_model, mood_intensity)

    # fallback
    if not answ or answ in [".", "..."]:
        answ = random.choice(fallback_msgs)

    print(f"Ada: {answ}") # resposta em texto da IA
    speak(answ, VOICE_REF, tts) # voz

    # Fila de mensagens
    conversation.append({"role": "user", "content": msg})
    conversation.append({"role": "assistant", "content": answ})

    if len(conversation) > 10: # mais que 10 mensagens + respostas -> sai 1 mensagem e 1 resposta
        conversation.pop(0)
        conversation.pop(0)

    decay_mood(mood_intensity)