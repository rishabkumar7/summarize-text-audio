from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from summarize import summarize_prompt
from google.cloud import texttospeech
#from google.cloud import storage

app = Flask(__name__)

def respond(message):
  response = MessagingResponse()
  response.message(message)
  return str(response)

# Instantiates a client
client = texttospeech.TextToSpeechClient()
#storage_client = storage.Client()

def summarize_audio(summary_txt):
  synthesis_input = texttospeech.SynthesisInput(text=summary_txt)

  voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
  )

  audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
  )

  response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
  )

  with open("resources/output.mp3", "wb") as out: 
      out.write(response.audio_content)
      print('Audio content written to file "output.mp3"')

@app.route("/summary", methods=['GET', 'POST'])
def incoming_sms():
    resp = MessagingResponse()
    msg = resp.message()
    user_input = request.form.get('NumMedia')
    if user_input == '1':
      pic_url = request.form.get('MediaUrl0')
      summary = summarize_prompt(pic_url)
      summarize_audio(summary)
      #upload_blob()
      #return respond(f"{summary}")
      msg.media("./resources/output.mp3")
      msg.body(f"{summary}")
      return str(resp), 200
    else:
      msg.body("Please send a picture containing text!")
      return str("Please send a picture containing text!")

@app.route("/resources/<path:path>")
def send_resources(path):
  return send_from_directory('resources', path)

if __name__ == "__main__":
   app.run(host='localhost', debug=True, port=8080)

