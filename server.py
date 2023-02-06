# Import flask 
from flask import Flask, request
from azure.cosmos import CosmosClient
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobClient
import nltk
from nltk.corpus import cmudict
import pyaudio
import wave
import azure.cognitiveservices.speech as speechsdk

nltk.download('cmudict')
pronouncer = cmudict.dict()

URL = 'https://glibzter-db.documents.azure.com:443/'
KEY = 'RWeSCZF5CUwdW85dQmcOEhnSOShgObBLSu4rPi7tKLwBkoU9uH5K3voOn3LSgac7hLzCEyNtl2EMACDb3fdaTg=='

connection_string = "DefaultEndpointsProtocol=https;AccountName=gamifiedchallengesb2ff;AccountKey=8utsv1UDT1oMy941pJrWle+axhvEHEIdgAEYb6PJUcl5nN8iT9VbNxKuekV4JwCMXfv1q+xuY0VL+AStH5g+kQ==;EndpointSuffix=core.windows.net"

client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'db1001'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'cont1001'
container = database.get_container_client(CONTAINER_NAME)

for item in container.query_items(
        query='SELECT r.word_1, r.word_2, r.word_3, r.word_4 FROM cont1001 r offset 0 limit 1',
        enable_cross_partition_query=True):
    #print(json.dumps(item, indent=True))
    #print(dict[item.values()])
    WORD_1 = list(item.values())[0]
    WORD_2 = list(item.values())[1]
    WORD_3 = list(item.values())[2]
    WORD_4 = list(item.values())[3]
    #print(WORD_4)
  
# Initializing flask app
app = Flask(__name__) 
  
# Route for seeing a data
@app.route('/data')
def get_words():
    
    #print(WORD_1)
    # Returning an api for showing in  reactjs
    return {
        "word_1": WORD_1, 
        "word_2": WORD_2,
        "word_3": WORD_3, 
        "word_4": WORD_4
        }

@app.route('/upload', methods=['POST'])
def upload():
    audio_data = request.data
    blob = BlobClient.from_connection_string(conn_str=connection_string, container_name="my-container", blob_name="audio_file_2_30_01")
    blob.upload_blob(audio_data)
    
    return "Audio uploaded successfully" 

@app.route('/assess')
def assess_pronunciation():
    nltk.download('cmudict')
    nltk.download('punkt')
    pronouncer = cmudict.dict()

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 30
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    audio_file = WAVE_OUTPUT_FILENAME
    
    speech_key, service_region = "d2a7943fa0eb4dfebbca5607f3dc8a4a", "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)

    reference_text = ""
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )
    speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, language="en-US", audio_config=audio_config)

    text = "Speaking into microphone"
    pronunciation_config.reference_text = text
    pronunciation_config.apply_to(speech_recognizer)

    result = speech_recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('Recognized: {}'.format(result.text))
        print('  Pronunciation Assessment Result:')

        pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
        #print(pronunciation_result.words)
        print('  Word-level details:')
        for idx, word in enumerate(pronunciation_result.words):
            print('    {}: word: {}, accuracy score: {}, error type: {};'.format(
                idx + 1, word.word, word.accuracy_score, word.error_type
            ))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    words = nltk.word_tokenize(text)
    for word in words:
        if word.lower() in pronouncer:
            phonemes = pronouncer[word.lower()][0]
            print(phonemes)
            # analyze the phonemes and compare to expected pronunciation

    return text

@app.route('/')
def home():
  
    return [WORD_1, WORD_2, WORD_3, WORD_4];
      
# Running app
if __name__ == '__main__':
    app.run(debug=True)