# Ada

**Companheira virtual de voz ou texto que não suporta ficar longe de você.**

Ada é uma assistente virtual que conversa por **texto ou voz**, usando IA local para entender e responder às mensagens.

## Requisitos

* **Python 3.13**
* Git
* **FFmpeg 9 full-shared**
* Microfone e saída de áudio
* Internet na primeira execução para baixar os modelos

### FFmpeg

O FFmpeg é necessário para o processamento de áudio. No Windows, baixe a versão **full-shared** do FFmpeg 9.

Extraia o conteúdo, por exemplo, em:

```text
C:\ffmpeg-9.0.1-full_build-shared
```

Depois, adicione a pasta `bin` ao PATH do Windows:

```powershell
setx PATH "$env:PATH;C:\ffmpeg-9.0.1-full_build-shared\bin"
```

**Feche e abra o terminal novamente** depois desse comando, pois o setx não atualiza o terminal atual.

Para verificar se o FFmpeg está funcionando:

```powershell
ffmpeg -version
```

Se aparecerem as informações da versão, está tudo certo.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/Saklas07/Ada.git
cd Ada
```

Crie e ative uma `venv`:

```bash
python -m venv venv
```

No PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

No CMD:

```cmd
venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executando

Com a `venv` ativada:

```bash
python main.py
```

Na primeira execução, os modelos de IA serão baixados automaticamente. Pode demorar um pouco.

## Uso

A Ada pode conversar por **texto ou voz**. Ao iniciar, informe seu nome e escolha o modo de conversa.

Para sair, use:

```text
sair
tchau
adeus
exit
quit
```

## Memória

As informações que a Ada conhece sobre o usuário ficam em `memory.json`.

Você pode editar esse arquivo para adicionar ou remover fatos e preferências.

## Voz

O arquivo `audio/voice_reference.wav` é usado como referência para gerar a voz da Ada.

**Não remova esse arquivo.**

## Estrutura

```text
Ada/
├── audio/
│   └── voice_reference.wav
├── funcs.py
├── main.py
├── memory.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Observação

A Ada roda os modelos localmente e atualmente está configurada para usar a **CPU**, então a velocidade pode variar bastante dependendo do computador.