from pydub import AudioSegment
from firebase_admin import credentials, firestore
import os

def upload_database_subcollection(collection_name, document_name, sub_collection_name, sub_document_name, field_name, new_value):
    cred = credentials.Certificate('./credentials.json')
    db = firestore.client()
    doc_ref = db.collection(collection_name).document(document_name).collection(sub_collection_name).document(sub_document_name)

    # Check if the document exists before updating it.
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            field_name: new_value
        })
    else:
        print(f"Error: Document {sub_document_name} does not exist in subcollection {sub_collection_name} of document {document_name} in collection {collection_name}.")



def upload_to_firestore(audio_data, sample_rate, filename):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name

        # Write the audio data to the WAV file
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono channel
            wav_file.setsampwidth(2)  # 16-bit depth
            wav_file.setframerate(sample_rate)
            # Convert the PyTorch tensor to a NumPy array before calling the tobytes method.
            wav_file.writeframes(audio_data.numpy().tobytes())

    project_id = "voice-clonning-b3160"
    client = storage.Client(project=project_id)
    bucket = client.bucket('voice-clonning-b3160.appspot.com')
    blob = bucket.blob('Voice-result/files/' + filename)
    blob.upload_from_filename(temp_path)
    os.remove(temp_path)
    return blob.public_url



def upload_audio(audio_data, sample_rate, new_file_name):
    url = upload_to_firestore(audio_data, sample_rate, new_file_name)
    return url


# Load the two audio files
music = AudioSegment.from_wav("/content/ZasmUXGY4elr.wav")
lyrics = AudioSegment.from_wav("/content/download (5).wav")

# Loop the music if its length is shorter than the lyrics
if len(music) < len(lyrics):
    music = music * (len(lyrics) // len(music) + 1)

# Reduce the volume of the music by 20 dB
music = music - 20

# Combine the two audio files
combined = music.overlay(lyrics)

# Export the combined audio to a new file
combined.export("/content/combined.wav", format='wav')

