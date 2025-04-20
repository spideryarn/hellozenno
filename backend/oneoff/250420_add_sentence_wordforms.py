#!/usr/bin/env python3
"""
This script adds wordforms and lemmas to the database for existing sentences.
This is needed to make the enhanced text feature work properly with structured data.
"""

import sys
import os

# Add the parent directory to Python path so we can import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import init_db
from db_models import Wordform, Lemma, Sentence, SentenceLemma
from peewee import fn
from loguru import logger
from utils.word_utils import extract_tokens, normalize_text

# Words to add for the Greek sentence 'Ο ανιψιός μου σπουδάζει ιατρική.'
WORDS_TO_ADD = [
    {
        "lemma": "ανιψιός",
        "translations": ["nephew"],
        "part_of_speech": "noun",
        "wordforms": [
            {
                "wordform": "ανιψιός",
                "translations": ["nephew"],
                "inflection_type": "nominative singular",
                "is_lemma": True
            }
        ]
    },
    {
        "lemma": "εγώ",
        "translations": ["I", "me"],
        "part_of_speech": "pronoun",
        "wordforms": [
            {
                "wordform": "μου",
                "translations": ["my", "mine"],
                "inflection_type": "genitive singular",
                "is_lemma": False
            }
        ]
    },
    {
        "lemma": "σπουδάζω",
        "translations": ["study", "learn"],
        "part_of_speech": "verb",
        "wordforms": [
            {
                "wordform": "σπουδάζει",
                "translations": ["studies", "is studying"],
                "inflection_type": "3rd person singular present",
                "is_lemma": False
            }
        ]
    },
    {
        "lemma": "ιατρική",
        "translations": ["medicine", "medical science"],
        "part_of_speech": "noun",
        "wordforms": [
            {
                "wordform": "ιατρική",
                "translations": ["medicine", "medical science"],
                "inflection_type": "nominative singular feminine",
                "is_lemma": True
            }
        ]
    }
]

def main():
    """Main function to execute the script"""
    init_db()
    
    # Process the sentence with slug "o-anipsios-mou-spoudazei-iatrike"
    sentence = Sentence.get_or_none(slug="o-anipsios-mou-spoudazei-iatrike")
    
    if not sentence:
        logger.error("Sentence not found")
        return
        
    logger.info(f"Processing sentence: {sentence.sentence}")
    
    # Add the lemmas and wordforms
    for word_data in WORDS_TO_ADD:
        # Create or update the lemma
        lemma, created = Lemma.update_or_create(
            lemma=word_data["lemma"],
            target_language_code=sentence.target_language_code,
            defaults={
                "translations": word_data["translations"],
                "part_of_speech": word_data["part_of_speech"],
                "is_complete": False,
                "commonality": 0.5,
                "guessability": 0.5,
            }
        )
        
        if created:
            logger.info(f"Created lemma: {lemma.lemma}")
        else:
            logger.info(f"Updated lemma: {lemma.lemma}")
            
        # Create wordforms for this lemma
        for wf_data in word_data["wordforms"]:
            wordform, wf_created = Wordform.update_or_create(
                wordform=wf_data["wordform"],
                target_language_code=sentence.target_language_code,
                defaults={
                    "lemma_entry": lemma,
                    "translations": wf_data["translations"],
                    "part_of_speech": word_data["part_of_speech"],
                    "inflection_type": wf_data["inflection_type"],
                    "is_lemma": wf_data["is_lemma"],
                }
            )
            
            if wf_created:
                logger.info(f"Created wordform: {wordform.wordform}")
            else:
                logger.info(f"Updated wordform: {wordform.wordform}")
        
        # Connect lemma to the sentence if not already connected
        sentence_lemma, sl_created = SentenceLemma.update_or_create(
            sentence=sentence,
            lemma=lemma
        )
        
        if sl_created:
            logger.info(f"Connected lemma {lemma.lemma} to sentence")
            
    logger.info("Done!")

if __name__ == "__main__":
    main()