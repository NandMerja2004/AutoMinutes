import yt_dlp
from pydub import AudioSegment
import os
import subprocess
import urllib.request
import zipfile
import shutil

DOWNLOAD_DIR='downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

BGUTIL_DIR = "/tmp/bgutil-ytdlp-pot-provider"
BGUTIL_SERVER = os.path.join(BGUTIL_DIR, "server")
BGUTIL_ZIP = "/tmp/bgutil-1.3.1.zip"


def setup_bgutil_provider():
    """Set up the bgutil PO-token provider."""

    if os.path.exists(
        os.path.join(BGUTIL_SERVER, "src", "generate_once.ts")
    ):
        return BGUTIL_SERVER

    print("Setting up bgutil PO-token provider...")

    if os.path.exists(BGUTIL_DIR):
        shutil.rmtree(BGUTIL_DIR)

    zip_url = (
        "https://github.com/Brainicism/"
        "bgutil-ytdlp-pot-provider/archive/refs/tags/1.3.1.zip"
    )

    urllib.request.urlretrieve(zip_url, BGUTIL_ZIP)

    with zipfile.ZipFile(BGUTIL_ZIP, "r") as zip_ref:
        zip_ref.extractall("/tmp")

    extracted_dir = "/tmp/bgutil-ytdlp-pot-provider-1.3.1"
    shutil.move(extracted_dir, BGUTIL_DIR)

    subprocess.run(
        [
            "deno",
            "install",
            "--allow-scripts=npm:canvas",
            "--frozen",
        ],
        cwd=BGUTIL_SERVER,
        check=True,
    )

    print("bgutil PO-token provider ready.")

    return BGUTIL_SERVER

def download_youtube_audio(url: str) -> str:
    bgutil_server = setup_bgutil_provider()

    output_path = os.path.join(
        DOWNLOAD_DIR, "%(title)s.%(ext)s"
    )

    ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": output_path,

    "extractor_args": {
        "youtube": {
            "player_client": ["mweb"]
        },
        "youtubepot-bgutilscript": {
            "server_home": bgutil_server
        }
    },

    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }
    ],

    "quiet": False,
    "verbose": True,
}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path:str, chunk_minutes:int=10)->list:
    audio= AudioSegment.from_wav(wav_path)
    chunk_ms=chunk_minutes * 60 * 1000
    chunks=[]
    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        
        chunks.append(chunk_path)
        
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks