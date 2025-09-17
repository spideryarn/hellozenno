from flask import Flask
from peewee import JOIN

from db_models import Sentence, SentenceAudio, database
from utils.db_connection import init_db
from utils.audio_utils import ensure_sentence_audio_variants


def main():
    # Initialize database connection
    init_db()

    app = Flask(__name__)

    try:
        sentences = (
            Sentence.select()
            .join(SentenceAudio, JOIN.LEFT_OUTER)
            .where(SentenceAudio.id.is_null(True))
        )
        print(f"Found {sentences.count()} sentences without variants")

        with app.app_context():
            with app.test_request_context():
                for sentence in sentences:
                    print(f"\nProcessing sentence ID {sentence.id}: {sentence.sentence}")
                    try:
                        ensure_sentence_audio_variants(
                            sentence,
                            enforce_auth=False,
                        )
                        print("✓ Audio variants ensured")
                    except Exception as e:
                        print(f"✗ Error ensuring audio: {e}")
    finally:
        # Always close the database connection
        if not database.is_closed():
            database.close()


if __name__ == "__main__":
    main()
