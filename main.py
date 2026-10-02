from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
import time
 
 
load_dotenv()
 
 
class PipelineCancelled(Exception):
    """Raised when the user stops the analysis."""
 
 
def run_pipeline(source: str, language: str = "english", on_progress=None, should_stop=None) -> dict:
    """
    on_progress(percent: float, message: str)  -> called before every stage
    should_stop() -> bool                        -> checked before every stage; True cancels the run
    Both are optional, so the CLI below keeps working unchanged.
    """
 
    def step(pct: float, msg: str):
        if should_stop and should_stop():
            raise PipelineCancelled()
        if on_progress:
            on_progress(pct, msg)
        else:
            print(msg)
 
    def pause(seconds: float = 1.2):
        # Rate-limit pause, split so a Stop request is noticed quickly
        end = time.time() + seconds
        while time.time() < end:
            if should_stop and should_stop():
                raise PipelineCancelled()
            time.sleep(0.1)
 
    step(3, "Preparing audio")
    chunks = process_input(source)
 
    # Transcribe chunk by chunk so progress moves during the longest stage (15% to 60%)
    parts = []
    total = max(len(chunks), 1)
    for i, chunk in enumerate(chunks):
        step(15 + 45 * i / total, f"Transcribing part {i + 1} of {total}")
        text = transcribe_all([chunk], language)
        parts.append(text)
    transcript = " ".join(parts)
 
    print(f"raw transcription (first 300 characters) {transcript[:300]}")
 
    step(62, "Writing a title")
    title = generate_title(transcript).replace("*", "").replace("`", "").strip().strip("\"'")
    pause()
 
    step(68, "Summarising")
    summary = summarize(transcript)
    pause()
 
    step(76, "Finding action items")
    action_item = extract_action_items(transcript)
    pause()
 
    step(84, "Extracting key decisions")
    decisions = extract_key_decisions(transcript)
    pause()
 
    step(91, "Collecting open questions")
    questions = extract_questions(transcript)
    pause()
 
    step(96, "Building the chat index")
    rag_chain = build_rag_chain(transcript)
 
    step(100, "Done")
    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_item,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }
 
 
if __name__ == "__main__":
    # CLI entry point
    source = input("Enter YouTube URL or local file path: ").strip()
    language = "english"
    result = run_pipeline(source, language)
 
    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)
 
    # Phase 2 — Chat with your meeting via RAG
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}\n")