from gtts import gTTS
import gradio as gr
import os
import speech_recognition as sr
from googletrans import Translator
from moviepy.editor import VideoFileClip, CompositeAudioClip, AudioFileClip
from pydub import AudioSegment
from pydub.playback import play

def video_to_translate(file_obj, initial_language, final_language):
    try:
        # Extract audio from video
        videoclip = VideoFileClip(file_obj.name)
        audio_path = "temp_audio.wav"
        videoclip.audio.write_audiofile(audio_path, codec='pcm_s16le')

        # Initialize recognizer
        r = sr.Recognizer()
        language_map = {
            "English": 'en-US',
            "Italian": 'it-IT',
            "Spanish": 'es-MX',
            "Russian": 'ru-RU',
            "German": 'de-DE',
            "Japanese": 'ja-JP',
            "Portuguese": 'pt-BR',
            "Kannada": 'kn-IN',
            "Gujarati": 'gu-IN',
            "Marathi": 'mr-IN',
            "Tamil": 'ta-IN',
            "Malayalam": 'ml-IN',
            "Telugu": 'te-IN',
            "Punjabi": 'pa-IN',
            "Bengali": 'bn-IN',
            "Bhojpuri": 'bho-IN'
        }

        # Open the audio file
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language=language_map[initial_language])

        # Translate text
        lang_map = {
            "English": 'en',
            "Italian": 'it',
            "Spanish": 'es',
            "Russian": 'ru',
            "German": 'de',
            "Japanese": 'ja',
            "Portuguese": 'pt',
            "Kannada": 'kn',
            "Gujarati": 'gu',
            "Marathi": 'mr',
            "Tamil": 'ta',
            "Malayalam": 'ml',
            "Telugu": 'te',
            "Punjabi": 'pa',
            "Bengali": 'bn',
            "Bhojpuri": 'bho'
        }

        translator = Translator()
        translation = translator.translate(text, dest=lang_map[final_language])
        trans_text = translation.text

        # Text to speech
        audio_output_path = "translated_audio.wav"
        tts = gTTS(text=trans_text, lang=lang_map[final_language], slow=False)
        tts.save(audio_output_path)

        # Synchronize the audio length
        original_audio = AudioSegment.from_wav(audio_path)
        translated_audio = AudioSegment.from_wav(audio_output_path)

        # Match the length of the translated audio to the original audio
        if len(translated_audio) < len(original_audio):
            translated_audio = translated_audio + AudioSegment.silent(duration=(len(original_audio) - len(translated_audio)))
        elif len(translated_audio) > len(original_audio):
            translated_audio = translated_audio[:len(original_audio)]

        translated_audio.export(audio_output_path, format="wav")

        # Add translated audio to video
        audioclip = AudioFileClip(audio_output_path)
        new_audioclip = CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        new_video = f"video_translated_{lang_map[final_language]}.mp4"
        videoclip.write_videofile(new_video)

        # Clean up temporary files
        os.remove(audio_path)
        os.remove(audio_output_path)

        return new_video
    except Exception as e:
        return str(e)

initial_language = gr.Dropdown(
    ["English", "Italian", "Japanese", "Russian", "Spanish", "German", "Portuguese", "Kannada", "Gujarati", "Marathi", "Tamil", "Malayalam", "Telugu", "Punjabi", "Bengali", "Bhojpuri"], 
    label="Initial Language"
)
final_language = gr.Dropdown(
    ["Russian", "Italian", "Spanish", "German", "English", "Japanese", "Portuguese", "Kannada", "Gujarati", "Marathi", "Tamil", "Malayalam", "Telugu", "Punjabi", "Bengali", "Bhojpuri"], 
    label="Final Language"
)

gr.Interface(
    fn=video_to_translate,
    inputs=[gr.File(), initial_language, final_language],
    outputs=gr.Video(),
    title='Video Translator',
    description='A simple application that translates video files. Upload your own file and wait for processing.',
    article='''
        <div>
            <p style="text-align: center"> All you need to do is to upload the mp4 file and hit submit, then wait for compiling. After that click on Play/Pause for listening to the video. The video is saved in an mp4 format.
            For more information visit <a href="https://ruslanmv.com/">ruslanmv.com</a>
            </p>
        </div>
    ''',
).launch()
