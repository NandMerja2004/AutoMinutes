import re
from faster_whisper import WhisperModel, BatchedInferencePipeline


# ============================================================
# Configuration
# ============================================================

# English-only Distil-Whisper model
WHISPER_MODEL = "base"

# CPU settings
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

# 4 is a safer default for ordinary CPU laptops.
# You can try 8 later if your laptop has enough RAM.
BATCH_SIZE = 4


# ============================================================
# Global model variables
# ============================================================

_whisper_model = None
_batched_model = None


# ============================================================
# Load Whisper model
# ============================================================

def load_whisper_model():
    global _whisper_model
    global _batched_model

    if _whisper_model is None:

        print("=" * 60)
        print("Loading faster-whisper...")
        print(f"Model      : {WHISPER_MODEL}")
        print(f"Device     : {DEVICE}")
        print(f"Compute    : {COMPUTE_TYPE}")
        print(f"Batch size : {BATCH_SIZE}")
        print("=" * 60)

        _whisper_model = WhisperModel(
            WHISPER_MODEL,
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
        )

        # Enable batched inference
        _batched_model = BatchedInferencePipeline(
            model=_whisper_model
        )

        # Correct model name in terminal
        print(
            f"faster-whisper {WHISPER_MODEL} "
            "loaded successfully."
        )

        print("Batched inference enabled.")

    return _batched_model


# ============================================================
# Clean non-English-script characters
# ============================================================

def clean_english_text(text: str) -> str:
    """
    Keep English/Latin text and remove non-Latin scripts
    such as Devanagari or Arabic/Urdu characters.
    """

    # Remove non-ASCII characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Remove excessive spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# Transcribe one audio chunk
# ============================================================

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
) -> str:

    model = load_whisper_model()

    print(f"Transcribing: {chunk_path}")

    segments, info = model.transcribe(
        chunk_path,

        # English only
        language="en",

        # Transcribe, don't translate
        task="transcribe",

        # Faster decoding
        beam_size=1,

        # Batched inference
        batch_size=BATCH_SIZE,

        # Skip silence
        vad_filter=True,

        # We only need text
        without_timestamps=True,

        # Each chunk is handled independently
        condition_on_previous_text=False,
    )

    text_parts = []

    for segment in segments:

        text = segment.text.strip()

        if not text:
            continue

        # Remove non-English scripts
        text = clean_english_text(text)

        if text:
            text_parts.append(text)

    return " ".join(text_parts).strip()


# ============================================================
# Transcribe all chunks
# ============================================================

def transcribe_all(
    chunks: list,
    language: str = "english"
) -> str:

    full_transcript = []

    print("=" * 60)
    print("Starting transcription")
    print(f"Model    : {WHISPER_MODEL}")
    print("Language : English")
    print(f"Chunks   : {len(chunks)}")
    print("=" * 60)

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing chunk "
            f"{i + 1}/{len(chunks)}..."
        )

        text = transcribe_chunk(
            chunk,
            language
        )

        if text:
            full_transcript.append(text)

    transcript = " ".join(full_transcript).strip()

    print("=" * 60)
    print("Transcription complete.")
    print(f"Transcript characters: {len(transcript)}")
    print("=" * 60)

    return transcript