import os
import yt_dlp
from pydub import AudioSegment


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio using a sequence of yt-dlp client strategies.
    Tries multiple clients because YouTube's availability can vary.
    """

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    strategies = [
    

        # 2. Safari/HLS route
        {
            "name": "web_safari",
            "extractor_args": {
                "youtube": {
                    "player_client": ["web_safari"]
                }
            }
        },

        # 3. TV client
        {
            "name": "tv",
            "extractor_args": {
                "youtube": {
                    "player_client": ["tv"]
                }
            }
        },

        # 4. Embedded client
        {
            "name": "web_embedded",
            "extractor_args": {
                "youtube": {
                    "player_client": ["web_embedded"]
                }
            }
        },
    ]

    last_error = None

    for strategy in strategies:

        print(f"\nTrying YouTube strategy: {strategy['name']}")

        ydl_opts = {
            "format": "bestaudio/best",

            "outtmpl": output_path,

            "extractor_args": strategy["extractor_args"],

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],

            "quiet": False,
            "verbose": True,

            # Don't let one failed format kill the whole strategy
            "ignoreerrors": False,

            # Network robustness
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 30,
        }

        try:

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(
                    url,
                    download=True
                )

                if not info:
                    raise RuntimeError(
                        "yt-dlp returned no video information."
                    )

                filename = ydl.prepare_filename(info)

                # yt-dlp postprocessor converts this to WAV
                possible_wav = os.path.splitext(filename)[0] + ".wav"

                if os.path.exists(possible_wav):
                    print(
                        f"SUCCESS: YouTube audio downloaded using "
                        f"{strategy['name']}"
                    )
                    return possible_wav

                # Sometimes the filename extension can differ
                base = os.path.splitext(filename)[0]

                for file in os.listdir(DOWNLOAD_DIR):
                    if file.startswith(
                        os.path.basename(base)
                    ) and file.endswith(".wav"):

                        return os.path.join(
                            DOWNLOAD_DIR,
                            file
                        )

        except Exception as e:

            last_error = e

            print(
                f"FAILED: {strategy['name']}"
            )

            print(
                f"Reason: {e}"
            )

            continue

    raise RuntimeError(
        "Unable to download this YouTube video using "
        "the available extraction methods.\n\n"
        f"Last error: {last_error}"
    )


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(input_path)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(
        output_path,
        format="wav"
    )

    return output_path


def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(
        range(0, len(audio), chunk_ms)
    ):

        chunk = audio[
            start:start + chunk_ms
        ]

        chunk_path = (
            f"{wav_path}_chunk_{i}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:

    if source.startswith(
        "http://"
    ) or source.startswith(
        "https://"
    ):

        print(
            "Detected YouTube URL. "
            "Trying available extraction methods..."
        )

        wav_path = download_youtube_audio(
            source
        )

    else:

        print(
            "Detected local file. "
            "Converting to WAV..."
        )

        wav_path = convert_to_wav(
            source
        )

    print("Chunking audio...")

    chunks = chunk_audio(
        wav_path
    )

    print(
        f"Audio ready - "
        f"{len(chunks)} chunk(s) created."
    )

    return chunks