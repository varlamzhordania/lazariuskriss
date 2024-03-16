# tasks.py
from celery import shared_task
from celery.result import AsyncResult
import re
import time


def count_sentences(text, language_name):
    # Define language-specific punctuation patterns for sentence splitting
    punctuation_patterns = {
        'Japanese': r'[！？。…‥]',
        'Korean': r'[.?!…,]',
        'English': r'[.?!…,]',
        # Add more languages as needed
    }

    # Get the punctuation pattern for the specified language
    punctuation_pattern = punctuation_patterns.get(language_name, r'[.!?]')

    # Tokenize the text into sentences using the punctuation pattern
    sentences = re.split(punctuation_pattern, text)

    # Filter out empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Return the count of sentences
    return len(sentences)


def check_payment_required(user_level, sentence_count):
    # Define maximum sentence counts for different user levels
    max_sentence_counts = {
        1: 1500,
        2: 3000,
        3: 7000,
        4: float('inf')  # No maximum for level 4
    }

    # Define the price multiplier for sentences over the maximum count
    price_multiplier = 0.052

    # Get the maximum sentence count for the user's level
    max_sentence_count = max_sentence_counts.get(user_level, 0)

    # Check if the actual sentence count exceeds the maximum count
    if sentence_count > max_sentence_count:
        # Calculate the additional payment required
        extra_sentences = sentence_count - max_sentence_count
        additional_payment = extra_sentences * price_multiplier
        return True, additional_payment
    else:
        return False, 0


@shared_task
def count_and_check_payment(username, language_name, title, text, user_level):
    try:
        # Check if the text already exists, existing text already set to false
        existing_text = False
        if existing_text:
            return {"message": "Text with the same title already exists.", "status": "error"}

        # Count sentences
        sentence_count = count_sentences(text, language_name)

        # Determine if payment is required
        payment_required, sentences_counts = check_payment_required(user_level, sentence_count)

        if payment_required:
            return {"message": "Payment is required.", "status": "payment_required", "sentence_count": sentences_counts}
        else:
            return {"message": "No payment required.", "status": "no_payment_required",
                    "sentence_count": sentences_counts}

    except Exception as e:
        return {"error": str(e), "status": "error"}


@shared_task
def process_text():
    print("Start processing text...")
    time.sleep(3)
    print("Finish processing text...")
    return {"message": "Process finished", "status": "success"}
