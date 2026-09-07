# =======================================
# Funções
# =======================================

import json  # Lê arquivos json
import os    # Interage com o sistema operacional
import torch # Modelos de IA
import whisper
import sounddevice as sd # Entrada/saída de áudio pelo microfone/alto-falante
import soundfile as sf   # Leitura/gravação de .wav
import numpy as np

whisper_model = whisper.load_model("base")

# Limpa console
def clear_terminal():
    print("\033[2J\033[H", end="")

# Sistema de Memória Simples (Lista de Fatos)
def fact_list(name):
    # Fatos essenciais que sempre devem estar no contexto
    common_facts = [
        f"O nome do usuário com quem você está falando é {name}."
    ]
    
    if os.path.exists("memory.json"):
        with open("memory.json", "r", encoding="utf-8") as f:
            saved_facts = json.load(f)
            # Junta a identidade base com as memórias do arquivo
            return common_facts + saved_facts.get("facts", []) + saved_facts.get("preferences", [])
            
    return common_facts

# Faz Ada ignorar certos caracteres ao falar
def clean_for_speech(text):
    return (
        text
        .replace("*", "")
        .replace("#", "")
        .replace("_", "")
    )

# Controla a Emoção Dominante da Ada
def speech_style(mood_intensity):
    # Retorna a key da emoção com maior intensidade
    mood = max(mood_intensity, key=mood_intensity.get)

    if mood_intensity[mood] <= 0:
        return "neutral"

    return mood

# Controla a escolha de palavras da Ada
def mood_prompt(mood_intensity):
    mood = speech_style(mood_intensity)
    styles = {
        "neutral": "Responda de forma natural e tranquila.",
        "happy": "Responda de forma alegre, animada e simpática.",
        "angry": "Responda de forma irritada e sarcástica, mas sem ser agressiva demais.",
        "sad": "Responda de forma mais triste, desanimada e introspectiva."
    }

    return styles[mood]

# Regula a emoção
def analyze_mood(text, mood_intensity, word_dict):
    text = text.lower()

    for mood, words in word_dict.items():
        mood = mood.replace("_words", "")

        for word in words:
            if word in text:
                mood_intensity[mood] += 1

    return mood_intensity

# Decai a emoção com o tempo
def decay_mood(mood_intensity):
    for mood in mood_intensity:
        mood_intensity[mood] *= 0.8

# Função para transformar voz em texto
def listen(username):
    print("\nOuvindo...")

    sample_rate = 16000
    block_duration = 0.1
    silence_limit = 1.5
    max_duration = 8.0
    threshold = 0.01

    blocks = []
    silence_time = 0
    recording_time = 0
    started_speaking = False

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    ) as stream:

        while recording_time < max_duration:
            audio, _ = stream.read(int(block_duration * sample_rate))

            blocks.append(audio.copy())
            recording_time += block_duration

            volume = np.sqrt(np.mean(audio ** 2))

            if volume >= threshold:
                started_speaking = True
                silence_time = 0
            elif started_speaking:
                silence_time += block_duration

            if started_speaking and silence_time >= silence_limit:
                break

    audio = np.concatenate(blocks)
    audio = np.squeeze(audio)

    #sf.write("debug.wav", audio, sample_rate)

    result = whisper_model.transcribe(
        audio,
        language="pt",
        task="transcribe"
    )

    text = result["text"].strip()

    print(f"{username}: {text}")

    return text

# Monta a resposta da Ada
def answer(user_text, facts_list, conversation, tokenizer, device, llm_model, mood_intensity):
    # Monta a persona com a lista de fatos
    system_prompt = (
        "Seu nome é Ada. "
        "Você é uma bela e charmosa mulher. "
        "Você é uma assistente virtual séria e inteligente. "
        "Responda sempre em português em 1 ou 2 frases curtas para falar em áudio. "
        + mood_prompt(mood_intensity) +
        "\nFatos que você sabe:\n"
        + "\n".join(f"- {f}" for f in facts_list)
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *conversation, # O * resgata todos os valores da lista
        {"role": "user", "content": user_text}
    ]

    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = llm_model.generate(**inputs, max_new_tokens=60, do_sample=True, temperature=1.0)
    
    answer_tokens = outputs[0][len(inputs.input_ids[0]):]
    answer_text = tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()
    return answer_text

# Cria arquivo de áudio e executa a voz
def speak(text, VOICE_REF, tts):
    file_output = "voice_out.wav"
    text_to_say = clean_for_speech(text)
    # Gera a fala imitando a voz de referência
    tts.tts_to_file(
        text=text_to_say,
        speaker_wav=VOICE_REF,
        language="pt",
        file_path=file_output
    )
    data, fs = sf.read(file_output)
    sd.play(data, fs)
    sd.wait()