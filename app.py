import os
from flask import Flask, request, render_template, jsonify, send_file
import whisper
import tempfile
from datetime import datetime
import time
import json
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['HISTORY_FILE'] = 'meeting_history.json'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Whisper model
model = whisper.load_model("base")

# Initialize Groq client
client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

def load_history():
    if os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(app.config['HISTORY_FILE'], 'w') as f:
        json.dump(history, f, indent=2)

def generate_minutes(text):
    # Create a prompt for the meeting minutes
    prompt = f"""Please create detailed meeting minutes from this transcript. Include the following sections:
1. Key Points
2. Action Items
3. Decisions Made
4. Discussion Details
5. Next Steps

Transcript:
{text}

Meeting Minutes:"""
    
    try:
        # Generate minutes using Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional meeting minutes compiler. Create clear, concise, and well-structured meeting minutes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        minutes = completion.choices[0].message.content
        
        # Format meeting minutes with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted_minutes = f"""MEETING MINUTES
================
Date: {timestamp}

{minutes}

MEETING ADJOURNED"""
        
        return formatted_minutes
    except Exception as e:
        print(f"Error generating minutes: {e}")
        # Fallback to basic format if AI generation fails
        return f"""MEETING MINUTES
================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}

TRANSCRIPT
---------
{text}

NOTES
-----
- Meeting duration: [To be added manually]
- Participants: [To be added manually]
- Next meeting: [To be added manually]"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def get_history():
    history = load_history()
    return jsonify(history)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        temp_file = None
        try:
            # Save the uploaded file temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
            file.save(temp_file.name)
            
            # Transcribe the audio
            result = model.transcribe(temp_file.name)
            transcript = result["text"]
            
            # Generate minutes
            minutes = generate_minutes(transcript)
            
            # Save to history
            history = load_history()
            history_entry = {
                'id': str(len(history)),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'filename': file.filename,
                'transcript': transcript,
                'minutes': minutes
            }
            history.append(history_entry)
            save_history(history)
            
            return jsonify({
                'transcript': transcript,
                'minutes': minutes,
                'history_id': history_entry['id']
            })
        except Exception as e:
            error_message = str(e)
            if "413" in error_message:
                error_message = "File size too large. Maximum file size is 100MB. Please try a smaller file."
            return jsonify({'error': error_message}), 500
        finally:
            # Clean up the temporary file after a short delay to ensure it's not in use
            if temp_file:
                try:
                    temp_file.close()
                    time.sleep(0.5)  # Give a small delay to ensure file is released
                    os.unlink(temp_file.name)
                except Exception as e:
                    print(f"Error cleaning up temporary file: {e}")

@app.route('/delete/<id>', methods=['DELETE'])
def delete_history_item(id):
    history = load_history()
    history = [item for item in history if item['id'] != id]
    save_history(history)
    return jsonify({'success': True})

@app.route('/download', methods=['POST'])
def download_file():
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'No content provided'}), 400
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write(content)
        temp_file.flush()
        
        # Send the file
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name='meeting_output.txt'
        )

if __name__ == '__main__':
    app.run(debug=True) 