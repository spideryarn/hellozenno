from api.db_models import Sentence, database
from utils.sentence_utils import generate_sentence
from utils.db_connection import init_db


def main():
    # Initialize database connection
    init_db()

    try:
        # Get all sentences without audio
        sentences = Sentence.select().where(Sentence.audio_data.is_null(True))
        print(f"Found {sentences.count()} sentences without audio")

        for sentence in sentences:
            print(f"\nProcessing: {sentence.sentence}")
            try:
                # Regenerate the sentence with audio
                generate_sentence(
                    target_language_code=sentence.language_code,
                    sentence=sentence.sentence,
                    translation=sentence.translation,
                    lemma_words=sentence.lemma_words,
                    should_play=False,
                )
                print("✓ Audio generated successfully")
            except Exception as e:
                print(f"✗ Error generating audio: {e}")
    finally:
        # Always close the database connection
        if not database.is_closed():
            database.close()


if __name__ == "__main__":
    main()
