from flask import Flask, render_template, jsonify
import speech_recognition as sr

app = Flask(__name__)

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Handle the speech-to-text transcription."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as inputs:
            print("Please speak now...")
            listening = recognizer.listen(inputs)
            print("Analyzing...")
            # Transcribe speech to Kannada text
            transcription = recognizer.recognize_google(listening, language="kn-IN")
            return jsonify({'status': 'success', 'text': transcription})
    except sr.UnknownValueError:
        return jsonify({'status': 'error', 'message': 'Could not understand the audio. Please try again.'})
    except sr.RequestError as e:
        return jsonify({'status': 'error', 'message': f'Error with the speech recognition service: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
