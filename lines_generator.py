# lines_generator.py

import json
import os
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Union
from shared_utils import find_best_folder_match

# (All constants and helper functions remain the same as the previous version)
# --- CONFIGURATION CONSTANTS ---
NUM_AIS = 16
NUM_TITLES_PER_AI = 8
NUM_SHORT_NAME_BLOCK_LINES = 9
NUM_DIALOGUE_LINES_PER_BLOCK = 34
DESCRIPTION_BLOCK_ANCHOR = "Beschreibung:"
DIALOGUE_KEYS = [
    "unknown_1", "taunt_1", "taunt_2", "taunt_3", "taunt_4", "anger_1", "anger_2", "plead", "nervous_1",
    "nervous_2", "victory_1", "victory_2", "victory_3", "victory_4", "request", "thanks", "ally_death",
    "congrats", "boast", "help", "extra", "kick_player", "add_player", "siege", "no_attack_1",
    "no_attack_2", "no_help_1", "no_help_2", "no_sent", "sent", "team_winning", "team_losing",
    "help_sent", "will_attack"
]
OUTPUT_KEYS_ORDER = [
    "ai_name", "newline", "title_1", "title_2", "title_3", "title_4", "title_5", "title_6", "title_7",
    "title_8", "newline", "complete_title_1", "complete_title_2", "complete_title_3", "complete_title_4",
    "complete_title_5", "complete_title_6", "complete_title_7", "complete_title_8", "newline",
    "description", "newline",
] + DIALOGUE_KEYS

# --- HELPER FUNCTIONS ---
def load_and_prepare_cr_data(filepath: str) -> Union[Tuple[List[str], List[str]], None]:
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.loads(f.read().replace(u'\u00A0', ' '))
        section_79 = next(s['SectionString'] for s in data if s['SectionIndex'] == 79)
        section_231 = next(s['SectionString'] for s in data if s['SectionIndex'] == 231)
        return section_79, section_231
    except (FileNotFoundError, json.JSONDecodeError, StopIteration) as e:
        print(f"  [Lines Generator] Warning: Could not load or find key sections in '{filepath}'. Details: {e}")
        return None

def parse_text_blocks(section_79, section_231) -> Union[List[Dict], None]:
    try:
        desc_anchor_index = section_79.index(DESCRIPTION_BLOCK_ANCHOR)
        descriptions = section_79[desc_anchor_index + 1 : desc_anchor_index + 1 + NUM_AIS]
        short_titles_block = section_79[desc_anchor_index - 1 - (NUM_AIS * NUM_SHORT_NAME_BLOCK_LINES) : desc_anchor_index - 1]
        complete_titles_block = section_79[desc_anchor_index - 1 - (NUM_AIS * NUM_SHORT_NAME_BLOCK_LINES) - (NUM_AIS * NUM_TITLES_PER_AI) : desc_anchor_index - 1 - (NUM_AIS * NUM_SHORT_NAME_BLOCK_LINES)]
        all_ai_data = []
        for i in range(NUM_AIS):
            short_chunk = short_titles_block[i * NUM_SHORT_NAME_BLOCK_LINES : (i + 1) * NUM_SHORT_NAME_BLOCK_LINES]
            complete_chunk = complete_titles_block[i * NUM_TITLES_PER_AI : (i + 1) * NUM_TITLES_PER_AI]
            dialogue_chunk = section_231[i * NUM_DIALOGUE_LINES_PER_BLOCK : (i + 1) * NUM_DIALOGUE_LINES_PER_BLOCK]
            ai_data = {'ai_name': short_chunk[0].strip(), 'description': descriptions[i].strip()}
            ai_data.update({f'title_{j+1}': title.strip() for j, title in enumerate(short_chunk[1:])})
            ai_data.update({f'complete_title_{j+1}': title.strip() for j, title in enumerate(complete_chunk)})
            ai_data.update({key: dialogue_chunk[j].strip() for j, key in enumerate(DIALOGUE_KEYS)})
            all_ai_data.append(ai_data)
        return all_ai_data
    except (ValueError, IndexError) as e:
        print(f"  [Lines Generator] Error: Failed to parse data blocks. File structure may be invalid. Details: {e}")
        return None

def write_formatted_lines_file(data: Dict, output_path: str):
    max_key_len = max(len(k) for k in OUTPUT_KEYS_ORDER if k != 'newline')
    output_lines = ["{"]
    last_key = next(k for k in reversed(OUTPUT_KEYS_ORDER) if k != 'newline')
    for key in OUTPUT_KEYS_ORDER:
        if key == "newline":
            output_lines.append("")
            continue
        value = data.get(key, "").replace('\\', '\\\\').replace('"', '\\"')
        line = f'  "{key}"'.ljust(max_key_len + 6) + f': "{value}"'
        if key != last_key: line += ","
        output_lines.append(line)
    output_lines.append("}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

# --- MAIN ENTRY POINT ---
def generate_lines_files(cr_json_path: str, existing_ai_folders: List[str], output_base_path: str) -> List[str]:
    """
    Main entry point to process a cr.json file.
    Returns a list of folder names for which a lines.json was successfully created.
    """
    print(f"\n--- Running Lines Generator for: {os.path.basename(cr_json_path)} ---")
    succeeded_folders = []
    
    prepared_data = load_and_prepare_cr_data(cr_json_path)
    if not prepared_data: return succeeded_folders

    parsed_ai_data = parse_text_blocks(prepared_data[0], prepared_data[1])
    if not parsed_ai_data: return succeeded_folders

    for ai_data in parsed_ai_data:
        ai_name_from_cr = ai_data['ai_name']
        matching_folder = find_best_folder_match(ai_name_from_cr, existing_ai_folders)

        if matching_folder:
            print(f"  - Processing '{ai_name_from_cr}': Matched to folder '{matching_folder}'.")
            final_output_dir = os.path.join(output_base_path, matching_folder)
            os.makedirs(final_output_dir, exist_ok=True)
            write_formatted_lines_file(ai_data, os.path.join(final_output_dir, 'lines.json'))
            succeeded_folders.append(matching_folder) # Track success
        else:
            print(f"  - Skipping '{ai_name_from_cr}': No matching character folder found.")
            
    return succeeded_folders