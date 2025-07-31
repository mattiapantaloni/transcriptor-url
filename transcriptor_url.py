import streamlit as st
import openai
import tempfile
import os
import yt_dlp
from moviepy.editor import VideoFileClip

# Leer la API key de OpenAI desde secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

st.title("Transcriptor de vídeos desde URL")

video_url = st.text_input("Introduce la URL del vídeo (Vimeo)")

if st.button("Transcribir"):
    if not video_url:
        st.warning("Por favor, introduce una URL.")
        st.stop()

    st.info("Extrayendo vídeo...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(tmpdir, 'video.%(ext)s'),
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                video_path = ydl.prepare_filename(info)

            st.success("Vídeo descargado. Extrayendo audio...")

            # Extraer audio
            video = VideoFileClip(video_path)
            audio_path = os.path.join(tmpdir, "audio.wav")
            video.audio.write_audiofile(audio_path)

            st.info("Transcribiendo con Whisper...")

            with open(audio_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)

            st.subheader("Transcripción completa:")
            st.write(transcript["text"])
            st.download_button("Descargar transcripción", transcript["text"], file_name="transcripcion.txt")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

