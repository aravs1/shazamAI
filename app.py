from flask import Flask, render_template, request, redirect, url_for
import os
import whisper
import tempfile
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

MEMORIES_FILE = "memories.txt"
whisper_model = None
semantic_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model for the first time...")
        whisper_model = whisper.load_model("base")
        print("Whisper model loaded.")
    return whisper_model

def get_semantic_model():
    global semantic_model
    if semantic_model is None:
        print("Loading semantic model for the first time...")
        semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Semantic model loaded.")
    return semantic_model

def get_memories():
    """Retrieves all memories from the memories file."""
    if not os.path.exists(MEMORIES_FILE):
        return []
    with open(MEMORIES_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def add_memory(memory_text):
    """Adds a memory to the memories file."""
    print(f"--> Attempting to add memory: '{memory_text}'")
    try:
        with open(MEMORIES_FILE, "a") as f:
            f.write(memory_text.strip() + "\n")
        print("--> Successfully wrote to memories.txt")
        return True
    except Exception as e:
        print(f"--> !!! ERROR WRITING TO FILE: {e}")
        return False

@app.route('/add_voice_memory', methods=['POST'])
def add_voice_memory():
    if 'audio_data' not in request.files:
        return "No audio file found", 400

    audio_file = request.files['audio_data']
    model = get_whisper_model()

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as temp_audio:
        audio_file.save(temp_audio.name)
        result = model.transcribe(temp_audio.name, fp16=False)
        transcribed_text = result["text"]

    if transcribed_text:
        add_memory(transcribed_text)
        return {"transcribed_text": transcribed_text}
    
    return {"transcribed_text": ""}, 400


def search_memories(search_term):
    """Searches for memories using both semantic similarity and keyword matching."""
    memories = get_memories()

    # On a blank search, return all memories
    if not search_term.strip():
        return memories

    if not memories:
        return []

    # 1. Keyword search
    keyword_results = {mem for mem in memories if search_term.lower() in mem.lower()}

    # 2. Semantic search
    model = get_semantic_model()
    query_embedding = model.encode(search_term, convert_to_tensor=True)
    corpus_embeddings = model.encode(memories, convert_to_tensor=True)
    
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    
    semantic_results = set()
    for idx, score in enumerate(cos_scores):
        if score > 0.4:  # Lowered threshold for better recall
            semantic_results.add(memories[idx])
            
    # 3. Combine results and return
    combined_results = list(keyword_results.union(semantic_results))
    return combined_results


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'add_memory' in request.form:
            memory = request.form['memory_text']
            if memory:
                add_memory(memory)
        return redirect(url_for('index'))

    search_term = request.args.get('search_term', '')
    memories = search_memories(search_term)
    return render_template('index.html', memories=memories, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)
