from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import os
import google.generativeai as genai
from gtts import gTTS
import uuid
from io import BytesIO
import base64

app = Flask(__name__)

# Configure Gemini AI
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 8192,
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

DIALECTS = [
    "Standard Kannada",
    "Dharwad Dialect",
    "Udupi Dialect",
    "Mysore Dialect",
    "Kodagu Dialect",
    "Brahmin Dialect"
]

# Ensure audio directory exists
audio_dir = 'temp_audio'
os.makedirs(audio_dir, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/realtime')
def realtime():
    return render_template('realtime.html', dialects=DIALECTS)

@app.route('/local')
def local():
    return render_template('local.html', dialects=DIALECTS)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'status': 'error', 'message': 'No audio file provided'})
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})
    
    try:
        # Save the uploaded file temporarily
        temp_path = os.path.join(audio_dir, 'temp_audio.wav')
        audio_file.save(temp_path)
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load the audio file and transcribe
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data, language="kn-IN")
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Use Gemini AI for dialect detection
        detect_prompt = f"""
        As a Kannada dialect expert, analyze this text and determine which dialect it matches best:
        
        Text: {transcription}
        
        Available dialects:
        - Standard Kannada
        - Dharwad Dialect
        - Udupi Dialect
        - Mysore Dialect
        - Kodagu Dialect
        - Brahmin Dialect
        
        Please provide:
        1. The detected dialect
        2. Confidence level (high/medium/low)
        3. Key dialect features identified
        4. Brief explanation of why this classification was made
        
        Format your response as:
        Detected Dialect: [name]
        Confidence: [level]
        Features: [list key features]
        Explanation: [your analysis]
        """
        
        response = model.generate_content(detect_prompt)
        
        return jsonify({
            'status': 'success',
            'transcription': transcription,
            'analysis': response.text
        })
        
    except sr.UnknownValueError:
        return jsonify({'status': 'error', 'message': 'Could not understand the audio'})
    except sr.RequestError as e:
        return jsonify({'status': 'error', 'message': f'Service error: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            transcription = recognizer.recognize_google(audio, language="kn-IN")
            
            # Detect dialect using Gemini
            prompt = f"""
            As a Kannada dialect expert, analyze this text and determine which dialect it matches:
            Text: {transcription}
            Available dialects: {', '.join(DIALECTS)}
            Provide your analysis and classification in this format:
            Detected Dialect: [dialect name]
            Explanation: [brief explanation of dialectal features]
            """
            
            response = model.generate_content(prompt)
            
            return jsonify({
                'status': 'success',
                'transcription': transcription,
                'analysis': response.text
            })
    except sr.UnknownValueError:
        return jsonify({'status': 'error', 'message': 'Could not understand audio'})
    except sr.RequestError as e:
        return jsonify({'status': 'error', 'message': f'Service error: {str(e)}'})

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    text = request.json.get('text')
    if not text:
        return jsonify({'status': 'error', 'message': 'No text provided'})
    
    try:
        # Create gTTS object with Kannada language and female voice
        tts = gTTS(text=text, lang='kn', slow=False)
        
        # Save to BytesIO buffer
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Convert to base64 for frontend
        audio_base64 = base64.b64encode(fp.read()).decode()
        
        return jsonify({
            'status': 'success',
            'audio': audio_base64
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/translate', methods=['POST'])
def translate():
    text = request.json.get('text')
    target_dialect = request.json.get('target_dialect')
    
    prompt = f"""
    Translate this Kannada text into {target_dialect}:
    Original text: {text}
    
    Consider the unique features of {target_dialect} including:
    - Vocabulary variations
    - Pronunciation patterns
    - Grammar differences
    
    Provide the translation with explanation of key dialectal changes.
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({'status': 'success', 'translation': response.text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)