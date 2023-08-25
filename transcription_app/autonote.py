import vercel_ai
import logging
import whisperx
import time
import sounddevice as sd
import numpy as np
import wavio

vercel_ai.logger.setLevel(logging.CRITICAL)
client = vercel_ai.Client()


def generate_notes(inp):
    prompt = f"Summarize this excerpt from a recording of a lecture or meeting using detailed, comprehensive, factual, and coherent bullet points: {inp}"
    params = {"maximumLength": 1200}
    max_retries = 50
    retry_delay = 1.1  # seconds

    for retry in range(max_retries):
        try:
            for chunk in client.generate("openai:gpt-3.5-turbo", prompt, params=params):
                print(chunk, end="", flush=True)
            print()
            break  # Success, exit the loop
        except Exception as e:
            print("Loading...")
            time.sleep(retry_delay)



def transcribe_audio(audio_file):
    device="cpu"
    batch_size=8
    compute_type="int8"
# 1. Transcribe with original whisper (batched)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)

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



def record_audio(filename="temp_recording.wav", duration=10, samplerate=44100):
    print("Recording audio... Please speak!")
    audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()  # Wait for the recording to finish
    print("Recording complete!")
    
    # Save recording to a WAV file
    wavio.write(filename, audio_data, samplerate, sampwidth=2)
    
    return filename

audio_filename = record_audio(duration=30)  # For a 30 second recording
generate_notes(transcribe_audio(audio_filename))
