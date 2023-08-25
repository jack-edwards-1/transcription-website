from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import vercel_ai
import logging
import whisperx
import time
import sounddevice as sd
import numpy as np
import wavio

from collections import deque

vercel_ai.logger.setLevel(logging.CRITICAL)
client = vercel_ai.Client()

recording_stream = None
audio_chunks = deque()
is_recording = False


def generate_notes(inp):
    prompt = f"Summarize this meeting transcript using detailed, comprehensive, factual, and coherent bullet points: {inp}"
    max_retries = 50
    retry_delay = 1.1  # seconds
    notes = ""
    for retry in range(max_retries):
        try:
            for chunk in client.generate("openai:gpt-3.5-turbo", prompt):
                notes+=chunk
            break  # Success, exit the loop
        except Exception as e:
            print("Loading...")
            time.sleep(retry_delay)
    return [inp.lstrip(),notes]



def transcribe_audio(audio_file):
    device="cpu"
    batch_size=8
    compute_type="int8"
# 1. Transcribe with original whisper (batched)
    model = whisperx.load_model("base", device, compute_type=compute_type)

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

# 3. Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token="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", device=device)

# add min/max number of speakers if known
    diarize_segments = diarize_model(audio)
# diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

    result = whisperx.assign_word_speakers(diarize_segments, result)

    current_speaker = ""
    output_text = ""
    for segment in result["segments"]: # segments are now assigned speaker IDs
        if not segment["speaker"] == current_speaker:
            current_speaker = segment["speaker"]
            output_text+=("\n"+segment["speaker"]+": "+segment["text"]+" ")
        else:
            output_text+=(segment["text"])
    return output_text


recording = None

def record_audio(command="start", filename="temp_recording.wav", samplerate=44100):
    global recording_stream, audio_chunks

    if command == "start":
        # Callback function to collect audio data
        def callback(indata, frames, time, status):
            audio_chunks.append(indata.copy())

        # Start the recording
        recording_stream = sd.InputStream(samplerate=samplerate, channels=1, callback=callback)
        recording_stream.start()
        return "Recording started"

    elif command == "stop" and recording_stream:
        recording_stream.stop()
        recording_stream.close()
        recording_stream = None

        # Combine all audio chunks
        audio_data = np.concatenate(list(audio_chunks), axis=0)
        audio_chunks.clear()

        # Save the recording to a WAV file
        wavio.write(filename, audio_data, samplerate, sampwidth=2)
        return filename
    else:
        return "No active recording"



@csrf_exempt
def demo(request):
    # Initialize the recording state for the session if it doesn't exist
    if 'recording_state' not in request.session:
        request.session['recording_state'] = 'stopped'
    return render(request, 'transcription_app/demo.html')

@csrf_exempt
def start_recording(request):
    global is_recording
    if not is_recording:
        record_audio(command="start")
        is_recording = True
        return HttpResponse("Recording started")
    else:
        return HttpResponse("Recording already in progress", status=400)

@csrf_exempt
def stop_recording(request):
    global is_recording
    if is_recording:
        audio_filename = record_audio(command="stop")
        notes = generate_notes(transcribe_audio(audio_filename))
        is_recording = False
        return JsonResponse({'transcript': notes[0], 'summary': notes[1]})
    else:
        return HttpResponse("No active recording", status=400)

@csrf_exempt
def homepage(request):
    return render(request, 'transcription_app/homepage.html')


import os
import subprocess
from django.conf import settings
from django.core.files.storage import FileSystemStorage


@csrf_exempt
def handle_uploaded_file(request):
    """
    Takes a file from the POST request, checks if it's a video or audio, 
    and saves the audio to the local filesystem.
    """
    
    # Check if there's a file in the request
    if 'myfile' not in request.FILES:
        return {"error": "No file uploaded."}

    file = request.FILES['myfile']
    fs = FileSystemStorage()

    # Save the uploaded file to the local filesystem
    filename = fs.save(file.name, file)
    file_url = fs.url(filename)
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    # Check if the file is a video based on its extension
    video_extensions = ['.mp4', '.mkv', '.avi', '.flv', '.mov']
    file_extension = os.path.splitext(file_path)[1]
    if file_extension in video_extensions:
        # Extract audio from the video
        output_audio_path = os.path.splitext(file_path)[0] + '.wav'
        command = ["ffmpeg", "-i", file_path, "-q:a", "0", "-map", "a", output_audio_path, "-y"]
        subprocess.run(command)

        # Delete the original video file to save space
        os.remove(file_path)
        file_path = output_audio_path
    notes = generate_notes(transcribe_audio(file_path))
    return JsonResponse({'transcript': notes[0], 'summary': notes[1]})
    

from django.shortcuts import render, redirect
from django.contrib import messages

def early_access(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Here, you can save the email to your database or send it to a mailing list.
        # For simplicity, I'm just showcasing the flow without actual storage.
        
        messages.success(request, 'Thanks for signing up! We will notify you once we launch.')
        return redirect('homepage')
