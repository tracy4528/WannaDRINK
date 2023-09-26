import openai

openai.api_key = "<你的 API Key>" 
audio_file= open("cropped.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
text = transcript.to_dict()['text']

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "說句話吧"}
    ]
)

print(text)
#抓當天熱門文章喂給onenapi 抓關鍵字回來