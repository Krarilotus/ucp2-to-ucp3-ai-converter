# shared_utils.py

import os
import re
from difflib import SequenceMatcher
from typing import Union

# --- CONSTANTS ---
# Why: Centralizing this map ensures consistent translation across the entire application.
GERMAN_TO_ENGLISH_NAMES = {
    "ratte": "rat", "schlange": "snake", "schwein": "pig", "wolf": "wolf", "saladin": "saladin",
    "kalif": "caliph", "sultan": "sultan", "richard löwenherz": "richard", "richard": "richard",
    "friedrich": "frederick", "kaiser friedrich": "frederick", "philipp": "phillip", "könig philipp": "phillip",
    "wesir": "wazir", "emir": "emir", "nizar": "nizar", "sheriff": "sheriff", "marschall": "marshal",
    "abt": "abbot", "könig": "king" # Added for cases like 'König' vs 'King Phillip'
}
ENGLISH_TO_GERMAN_NAMES = {v: k for k, v in GERMAN_TO_ENGLISH_NAMES.items()}


# --- FUNCTIONS ---

def sanitize_name(name: str) -> str:
    """
    Sanitizes a string for use as a file or folder name.
    Why: Ensures cross-system compatibility by replacing German umlauts and removing special characters.
    """
    if not name: return ""
    # Why: This order of operations (transliterate, then remove others) is crucial for correctness.
    name = name.replace('ä', 'ae').replace('Ä', 'Ae')
    name = name.replace('ö', 'oe').replace('Ö', 'Oe')
    name = name.replace('ü', 'ue').replace('Ü', 'Ue')
    name = name.replace('ß', 'ss')
    sane_name = re.sub(r'[^\w\s]', '', name)
    return sane_name.replace(' ', '')


def find_best_folder_match(name_to_match: str, existing_folders: list) -> Union[str, None]:
    """
    Finds the best matching folder using a multi-step, robust strategy.
    Why: This function provides a single source of truth for all name matching, ensuring
         that direct, sanitized, translated, and fuzzy matches are handled consistently.
    """
    # Strategy 1: Direct match on the sanitized name. (e.g., "König" -> "koenig" matches "Koenig" folder)
    sanitized_target = sanitize_name(name_to_match).lower()
    for folder in existing_folders:
        if folder.lower() == sanitized_target:
            return folder

    # Strategy 2: Match on language variations of the original name. (e.g., "Ratte" matches "Rat" folder)
    clean_original = name_to_match.lower().strip()
    variations = {clean_original}
    if clean_original in GERMAN_TO_ENGLISH_NAMES:
        variations.add(GERMAN_TO_ENGLISH_NAMES[clean_original])
    if clean_original in ENGLISH_TO_GERMAN_NAMES:
        variations.add(ENGLISH_TO_GERMAN_NAMES[clean_original])
    for folder in existing_folders:
        if folder.lower() in variations:
            return folder

    # Strategy 3: Fallback to fuzzy matching using the sanitized name.
    best_match_folder = None
    max_match_length = 3  # A match must have at least 4 common characters.
    for folder in existing_folders:
        clean_folder = folder.lower()
        matcher = SequenceMatcher(None, sanitized_target, clean_folder)
        match = matcher.find_longest_match(0, len(sanitized_target), 0, len(clean_folder))
        if match.size > max_match_length:
            max_match_length = match.size
            best_match_folder = folder
            
    return best_match_folder