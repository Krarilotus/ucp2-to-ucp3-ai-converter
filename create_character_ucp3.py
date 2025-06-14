# create_character_ucp3.py

import os
import json
import re
import sys
import shutil
import argparse
from typing import Union, Dict, List
# Import our own modules for cleaner code organization.
import lines_generator
from shared_utils import sanitize_name, find_best_folder_match

# --- CONFIGURATION CONSTANTS ---
# Centralizing all paths makes the script easy to configure and read.
AIV_INPUT_DIR = os.path.join("UCP", "resources", "aiv")
AIC_INPUT_DIR = os.path.join("UCP", "resources", "aic")
TROOPS_INPUT_DIR = os.path.join("UCP", "resources", "troops")
CR_INPUT_DIR = os.path.join("UCP", "resources", "cr")
PORTRAITS_INPUT_DIR = os.path.join("UCP", "resources", "portraits")
SPEECH_INPUT_DIR = os.path.join("UCP", "resources", "speech")
BINKS_INPUT_DIR = os.path.join("UCP", "resources", "binks")
OUTPUT_AI_DIR = os.path.join("resources", "ai")

# This provides a reliable mapping from the fixed troop index to the vanilla AI name.
TROOP_INDEX_TO_NAME = {
    "1": "Rat", "2": "Snake", "3": "Pig", "4": "Wolf", "5": "Saladin", "6": "Caliph", 
    "7": "Sultan", "8": "Richard", "9": "Frederick", "10": "Phillip", "11": "Wazir", 
    "12": "Emir", "13": "Nizar", "14": "Sheriff", "15": "Marshal", "16": "Abbot",
}
# This reverse map is needed to calculate asset numbers based on the vanilla AI name.
NAME_TO_AI_INDEX = {name: int(index) for index, name in TROOP_INDEX_TO_NAME.items()}


# --- SPEECH CONFIGURATION ---
LORD_PREFIX_MAP = {
    "Saladin": "sa", "Caliph": "ca", "Sultan": "su", "Richard": "ri", "Frederick": "fr", 
    "Phillip": "ph", "Wazir": "wa", "Emir": "em", "Nizar": "ni", "Sheriff": "sh", 
    "Marshal": "ma", "Abbot": "ab"
}
SPECIAL_SPEECH_MAP = {
    "Rat": {"taunt_1": "rt_taunt_01.wav", "taunt_2": "rt_taunt_02.wav", "taunt_3": "rt_taunt_05.wav", "taunt_4": "rt_taunt_08.wav", "anger_1": "rt_anger_04.wav", "anger_2": "rt_anger_01.wav", "plead": "rt_plead_01.wav", "nervous_1": "rt_plead_04.wav", "nervous_2": "rt_plead_03.wav", "victory_1": "rt_vict_01.wav", "victory_2": "rt_vict_02.wav", "victory_3": "rt_vict_04.wav", "victory_4": "rt_vict_03.wav", "ally_death": "rt_anger_02.wav", "kick_player": "rt_kick_player.wav", "add_player": "rt_add_player.wav"},
    "Snake": {"taunt_1": "sn_taunt_01.wav", "taunt_2": "sn_taunt_04.wav", "taunt_3": "sn_taunt_05.wav", "taunt_4": "sn_taunt_07.wav", "anger_1": "sn_anger_03.wav", "anger_2": "sn_anger_04.wav", "plead": "sn_plead_01.wav", "nervous_1": "sn_plead_04.wav", "nervous_2": "sn_plead_03.wav", "victory_1": "sn_vict_02.wav", "victory_2": "sn_taunt_03.wav", "victory_3": "sn_vict_03.wav", "victory_4": "sn_vict_04.wav", "ally_death": "all_ally_death_01.wav", "kick_player": "sn_kick_player.wav", "add_player": "sn_add_player.wav"},
    "Pig": {"taunt_1": "pg_taunt_03.wav", "taunt_2": "pg_taunt_04.wav", "taunt_3": "pg_taunt_06.wav", "taunt_4": "pg_taunt_07.wav", "anger_1": "pg_anger_04.wav", "anger_2": "pg_anger_02.wav", "plead": "pg_plead_01.wav", "nervous_1": "pg_plead_03.wav", "nervous_2": "pg_plead_04.wav", "victory_1": "pg_vict_01.wav", "victory_2": "pg_vict_02.wav", "victory_3": "pg_vict_03.wav", "victory_4": "pg_taunt_02.wav", "ally_death": "pg_plead_02.wav", "kick_player": "pg_kick_player.wav", "add_player": "pg_add_player.wav"},
    "Wolf": {"taunt_1": "wf_taunt_01.wav", "taunt_2": "wf_taunt_02.wav", "taunt_3": "wf_taunt_05.wav", "taunt_4": "wf_taunt_06.wav", "anger_1": "wf_anger_04.wav", "anger_2": "wf_anger_02.wav", "plead": "wf_plead_01.wav", "nervous_1": "wf_plead_03.wav", "nervous_2": "wf_plead_04.wav", "victory_1": "wf_vict_02.wav", "victory_2": "wf_taunt_04.wav", "victory_3": "wf_vict_01.wav", "victory_4": "all_vict_04.wav", "ally_death": "all_ally_death_01.wav", "kick_player": "wf_kick_player.wav", "add_player": "wf_add_player.wav"}
}
SHARED_FILES_FOR_FIRST_FOUR = { "request": "all_req_01.wav", "thanks": "all_thanks_01.wav", "congrats": "all_congrats_01.wav", "boast": "all_boast_01.wav", "help": "all_help_01.wav", "extra": "all_extra_01.wav", "siege": "all_siege_01.wav", "no_attack_1": "all_noattack_01.wav", "no_attack_2": "all_noattack_02.wav", "no_help_1": "all_nohelp_01.wav", "no_help_2": "all_nohelp_02.wav", "no_sent": "all_notsent_01.wav", "sent": "all_sent_01.wav", "team_winning": "all_team_winning_01.wav", "team_losing": "all_team_losing_01.wav", "help_sent": "all_helpsent_01.wav", "will_attack": "all_willattack_01.wav" }
for lord in ["Rat", "Snake", "Pig", "Wolf"]:
    for key, filename in SHARED_FILES_FOR_FIRST_FOUR.items():
        if key not in SPECIAL_SPEECH_MAP[lord]: SPECIAL_SPEECH_MAP[lord][key] = filename
FILENAME_STEM_TO_KEY_MAP = { "taunt_01": "taunt_1", "taunt_02": "taunt_2", "taunt_03": "taunt_3", "taunt_04": "taunt_4", "anger_01": "anger_1", "anger_02": "anger_2", "plead_01": "plead", "nervous_01": "nervous_1", "nervous_02": "nervous_2", "vict_01": "victory_1", "vict_02": "victory_2", "vict_03": "victory_3", "vict_04": "victory_4", "req_01": "request", "thanks_01": "thanks", "ally_death_01": "ally_death", "congrats_01": "congrats", "boast_01": "boast", "help_01": "help", "extra_01": "extra", "kick_player_01": "kick_player", "add_player_01": "add_player", "siege_01": "siege", "noattack_01": "no_attack_1", "noattack_02": "no_attack_2", "nohelp_01": "no_help_1", "nohelp_02": "no_help_2", "notsent_01": "no_sent", "sent_01": "sent", "team_winning_01": "team_winning", "team_losing_01": "team_losing", "helpsent_01": "help_sent", "willattack_01": "will_attack" }

# --- BINKS CONFIGURATION ---
BINKS_CONFIG = {
    "Saladin": {"prefix": "saladin_"}, "Caliph": {"prefix": "bad_arab_"}, "Sultan": {"prefix": "sultan_"},
    "Richard": {"prefix": "richard_"}, "Frederick": {"prefix": "fred_"}, "Phillip": {"prefix": "philip_"},
    "Wazir": {"prefix": "vizir_"}, "Emir": {"prefix": "emir_"}, "Nizar": {"prefix": "nazir_"},
    "Sheriff": {"prefix": "sheriff_"}, "Marshal": {"prefix": "ma_"}, "Abbot": {"prefix": "abbot_"},
    "Rat": {"mapping": { "taunt_1": "rt_taunt2.bik", "taunt_2": "rt_taunt1.bik", "taunt_3": "rt_taunt2.bik", "taunt_4": "rt_taunt1.bik", "anger_1": "rt_anger1.bik", "anger_2": "rt_anger1.bik", "plead": "rt_plead1.bik", "nervous_1": "rt_plead2.bik", "nervous_2": "rt_plead3.bik", "victory_1": "rt_vict1.bik", "victory_2": "rt_vict1.bik", "victory_3": "rt_vict1.bik", "victory_4": "rt_vict1.bik", "request": "bad_soldier_taunt.bik", "thanks": "bad_soldier_taunt.bik", "ally_death": "rt_anger1.bik", "congrats": "bad_soldier_taunt.bik", "boast": "bad_soldier_taunt.bik", "help": "bad_soldier_nevous.bik", "extra": "bad_soldier_taunt.bik", "siege": "bad_soldier_taunt.bik", "no_attack_1": "bad_soldier_nevous.bik", "no_attack_2": "bad_soldier_taunt.bik", "no_help_1": "bad_soldier_taunt.bik", "no_help_2": "bad_soldier_taunt.bik", "no_sent": "bad_soldier_taunt.bik", "sent": "bad_soldier_taunt.bik", "team_losing": "bad_soldier_nevous.bik", "team_winning": "bad_soldier_taunt.bik", "help_sent": "bad_soldier_taunt.bik", "will_attack": "bad_soldier_taunt.bik"}},
    "Snake": {"mapping": { "taunt_1": "sn_taunt1.bik", "taunt_2": "sn_taunt2.bik", "taunt_3": "sn_taunt1.bik", "taunt_4": "sn_taunt2.bik", "anger_1": "sn_anger1.bik", "anger_2": "sn_anger1.bik", "plead": "sn_plead2.bik", "nervous_1": "sn_plead2.bik", "nervous_2": "sn_plead2.bik", "victory_1": "sn_vict2.bik", "victory_2": "sn_vict1.bik", "victory_3": "sn_vict1.bik", "victory_4": "sn_taunt1.bik", "request": "bad_soldier_taunt.bik", "thanks": "bad_soldier_taunt.bik", "ally_death": "bad_soldier_nevous.bik", "congrats": "bad_soldier_taunt.bik", "boast": "bad_soldier_taunt.bik", "help": "bad_soldier_nevous.bik", "extra": "bad_soldier_taunt.bik", "siege": "bad_soldier_taunt.bik", "no_attack_1": "bad_soldier_nevous.bik", "no_attack_2": "bad_soldier_taunt.bik", "no_help_1": "bad_soldier_taunt.bik", "no_help_2": "bad_soldier_taunt.bik", "no_sent": "bad_soldier_taunt.bik", "sent": "bad_soldier_taunt.bik", "team_losing": "bad_soldier_nevous.bik", "team_winning": "bad_soldier_taunt.bik", "help_sent": "bad_soldier_taunt.bik", "will_attack": "bad_soldier_taunt.bik"}},
    "Pig": {"mapping": { "taunt_1": "pg_taunt1.bik", "taunt_2": "pg_taunt2.bik", "taunt_3": "pg_taunt1.bik", "taunt_4": "pg_taunt2.bik", "anger_1": "pg_anger1.bik", "anger_2": "pg_anger1.bik", "plead": "pg_plead1.bik", "nervous_1": "pg_plead2.bik", "nervous_2": "pg_plead1.bik", "victory_1": "pg_vict1.bik", "victory_2": "pg_vict2.bik", "victory_3": "pg_vict3.bik", "victory_4": "pg_vict1.bik", "request": "bad_soldier_taunt.bik", "thanks": "bad_soldier_taunt.bik", "ally_death": "pg_plead1.bik", "congrats": "bad_soldier_taunt.bik", "boast": "bad_soldier_taunt.bik", "help": "bad_soldier_nevous.bik", "extra": "bad_soldier_taunt.bik", "siege": "bad_soldier_taunt.bik", "no_attack_1": "bad_soldier_nevous.bik", "no_attack_2": "bad_soldier_taunt.bik", "no_help_1": "bad_soldier_taunt.bik", "no_help_2": "bad_soldier_taunt.bik", "no_sent": "bad_soldier_taunt.bik", "sent": "bad_soldier_taunt.bik", "team_losing": "bad_soldier_nevous.bik", "team_winning": "bad_soldier_taunt.bik", "help_sent": "bad_soldier_taunt.bik", "will_attack": "bad_soldier_taunt.bik"}},
    "Wolf": {"mapping": { "taunt_1": "wf_taunt1.bik", "taunt_2": "wf_taunt2.bik", "taunt_3": "wf_taunt1.bik", "taunt_4": "wf_taunt2.bik", "anger_1": "wf_anger1.bik", "anger_2": "wf_anger1.bik", "plead": "wf_plead1.bik", "nervous_1": "wf_plead2.bik", "nervous_2": "wf_plead1.bik", "victory_1": "wf_vict1.bik", "victory_2": "wf_vict2.bik", "victory_3": "wf_vict1.bik", "victory_4": "bad_soldier_taunt.bik", "request": "bad_soldier_taunt.bik", "thanks": "bad_soldier_taunt.bik", "ally_death": "bad_soldier_nevous.bik", "congrats": "bad_soldier_taunt.bik", "boast": "bad_soldier_taunt.bik", "help": "bad_soldier_nevous.bik", "extra": "bad_soldier_taunt.bik", "siege": "bad_soldier_taunt.bik", "no_attack_1": "bad_soldier_nevous.bik", "no_attack_2": "bad_soldier_taunt.bik", "no_help_1": "bad_soldier_taunt.bik", "no_help_2": "bad_soldier_taunt.bik", "no_sent": "bad_soldier_taunt.bik", "sent": "bad_soldier_taunt.bik", "team_losing": "bad_soldier_nevous.bik", "team_winning": "bad_soldier_taunt.bik", "help_sent": "bad_soldier_taunt.bik", "will_attack": "bad_soldier_taunt.bik"}}
}
STANDARD_BINKS_MAPPING = { "taunt_1": "taunting", "taunt_2": "taunting", "taunt_3": "taunting", "taunt_4": "taunting", "anger_1": "nervous", "anger_2": "nervous", "plead": "nervous", "nervous_1": "nervous", "nervous_2": "anger", "victory_1": "natural", "victory_2": "taunting", "victory_3": "natural", "victory_4": "natural", "request": "natural", "thanks": "natural", "ally_death": "nervous", "congrats": "natural", "boast": "taunting", "help": "nervous", "extra": "natural", "siege": "taunting", "no_attack_1": "nervous", "no_attack_2": "nervous", "no_help_1": "nervous", "no_help_2": "nervous", "no_sent": "nervous", "sent": "natural", "team_losing": "nervous", "team_winning": "taunting", "help_sent": "natural", "will_attack": "natural" }


# --- HELPER & LOGIC FUNCTIONS ---

def write_aligned_json(data: Dict, output_path: str):
    """Writes a dictionary to a JSON file with aligned colons for readability."""
    if not data: return
    # Calculate the required padding based on the longest key.
    max_key_len = max(len(k) for k in data.keys())
    # The padding accounts for indent, quotes, and space around the colon.
    key_padding = max_key_len + 4
    
    output_lines = ["{"]
    items = list(data.items())
    for i, (key, value) in enumerate(items):
        # Format the line with left-justified padding.
        left_part = f'  "{key}"'
        line = f'{left_part.ljust(key_padding)}: "{value}"'
        # Add a comma to all lines except the very last one.
        if i < len(items) - 1:
            line += ","
        output_lines.append(line)
    output_lines.append("}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

def load_all_troop_data(troops_path: str) -> dict:
    """Loads all troop JSON files into a single dictionary, keyed by vanilla AI name."""
    all_troops = {}
    print(f"Loading troop data from '{troops_path}'...")
    for filename in os.listdir(troops_path):
        if not filename.endswith('.json'): continue
        with open(os.path.join(troops_path, filename), 'r', encoding='utf-8-sig') as f:
            for index, troop_info in json.load(f).items():
                if index in TROOP_INDEX_TO_NAME:
                    all_troops[TROOP_INDEX_TO_NAME[index]] = troop_info
    print(f"Successfully loaded troop data for {len(all_troops)} lords.")
    return all_troops

def process_aiv_files(original_name, output_name, char_output_dir, source_path) -> bool:
    """Finds, copies, renames, and maps AIV files for a single character."""
    if not source_path or not os.path.isdir(source_path): return False
    files_to_copy = []
    for filename in os.listdir(source_path):
        if re.match(f"^{original_name.lower()}(\\d+)\\.aiv$", filename.lower()):
            files_to_copy.append(filename)
    if not files_to_copy: return False
    
    output_dir = os.path.join(char_output_dir, "aiv")
    os.makedirs(output_dir, exist_ok=True)
    mappings = {}
    for filename in files_to_copy:
        number = re.match(f"^{original_name.lower()}(\\d+)\\.aiv$", filename.lower()).group(1)
        new_filename = f"{output_name.lower()}{number}.aiv"
        shutil.copy2(os.path.join(source_path, filename), os.path.join(output_dir, new_filename))
        mappings[f"castle_{number}"] = new_filename
    with open(os.path.join(output_dir, "mapping.json"), 'w', encoding='utf-8') as f: json.dump(mappings, f, indent=2)
    print(f"    ├─ Found and processed AIV files, created mapping.json")
    return True

def process_portrait_files(original_name: str, char_output_dir: str, source_path: str) -> bool:
    """Finds, copies, and renames the portrait images for a character."""
    if not source_path or not os.path.isdir(source_path): return False
    ai_index = NAME_TO_AI_INDEX.get(original_name)
    if not ai_index: return False
    large_src = os.path.join(source_path, f"Image{522 + ai_index}.png")
    small_src = os.path.join(source_path, f"Image{700 + ai_index}.png")
    portraits_found = False
    if os.path.exists(large_src):
        shutil.copy2(large_src, os.path.join(char_output_dir, "portrait.png")); portraits_found = True
    if os.path.exists(small_src):
        shutil.copy2(small_src, os.path.join(char_output_dir, "portrait_small.png")); portraits_found = True
    if portraits_found: print(f"    ├─ Found and processed portrait files.")
    return portraits_found

def process_speech_files(original_name, output_name, char_output_dir, source_path) -> bool:
    """Dynamically finds, copies, and maps speech files based on the AI type."""
    if not source_path or not os.path.isdir(source_path): return False
    final_mappings, files_to_copy = {}, []
    
    # Check if the current AI has a special, hardcoded mapping.
    if original_name in SPECIAL_SPEECH_MAP:
        speech_map = SPECIAL_SPEECH_MAP[original_name]
        for key, source_filename in speech_map.items():
            if os.path.exists(os.path.join(source_path, source_filename)):
                files_to_copy.append((key, source_filename))
    # Otherwise, process it as a standard lord by scanning for files with a known prefix.
    elif original_name in LORD_PREFIX_MAP:
        prefix = LORD_PREFIX_MAP[original_name]
        for filename in os.listdir(source_path):
            if filename.lower().startswith(prefix + "_"):
                stem = filename[len(prefix)+1:].replace('.wav', '')
                key = FILENAME_STEM_TO_KEY_MAP.get(stem)
                if key: files_to_copy.append((key, filename))

    # The General_Message file is handled consistently for all lords.
    ai_index = NAME_TO_AI_INDEX.get(original_name)
    if ai_index:
        gm_filename = f"General_Message{22 + ai_index}.wav"
        if original_name in ["Pig", "Wolf"]: gm_filename = SPECIAL_SPEECH_MAP[original_name].get("message_from", gm_filename)
        if os.path.exists(os.path.join(source_path, gm_filename)):
            files_to_copy.append(("message_from", gm_filename))
            
    if not files_to_copy: return False
    output_dir = os.path.join(char_output_dir, "speech")
    os.makedirs(output_dir, exist_ok=True)
    for key, source_filename in files_to_copy:
        prefix, _, suffix = source_filename.partition('_')
        new_filename = f"{output_name.lower()}_{suffix}" if suffix else f"{output_name.lower()}_{source_filename}"
        if key == "message_from": new_filename = f"General_Message_{output_name.lower()}.wav"
        shutil.copy2(os.path.join(source_path, source_filename), os.path.join(output_dir, new_filename))
        final_mappings[key] = new_filename
        
    write_aligned_json(final_mappings, os.path.join(output_dir, "mapping.json"))
    print(f"    ├─ Found and processed speech files, created mapping.json")
    return True

def process_binks_files(original_name: str, output_name: str, char_output_dir: str, source_path: str) -> bool:
    """Finds, copies, renames, and maps all Bink video files for a character."""
    if not source_path or not os.path.isdir(source_path): return False
    config = BINKS_CONFIG.get(original_name)
    if not config: return False
    final_mappings, files_found = {}, False
    
    # The logic is split to handle standard lords vs. the unique first four.
    if "prefix" in config:
        mood_map = {"anger": "anger", "angry": "anger", "taunt": "taunting", "taunting": "taunting", "confident": "taunting", "nervous": "nervous", "natural": "natural"}
        found_videos = {} 
        for filename in os.listdir(source_path):
            if filename.lower().startswith(config["prefix"]):
                mood_stem = filename.lower().replace(config["prefix"], "").replace(".bik", "")
                if mood_stem in mood_map:
                    if not files_found: # Create directory only when the first file is found.
                        os.makedirs(os.path.join(char_output_dir, "binks"), exist_ok=True); files_found = True
                    standard_mood = mood_map[mood_stem]
                    new_filename = f"{output_name.lower()}_{standard_mood}.bik"
                    found_videos[standard_mood] = new_filename
                    shutil.copy2(os.path.join(source_path, filename), os.path.join(char_output_dir, "binks", new_filename))
        for key, mood in STANDARD_BINKS_MAPPING.items():
            if mood in found_videos: final_mappings[key] = found_videos[mood]
    elif "mapping" in config:
        copied_files = {} 
        for key, source_filename in config["mapping"].items():
            source_file = os.path.join(source_path, source_filename)
            if source_file not in copied_files and os.path.exists(source_file):
                if not files_found:
                    os.makedirs(os.path.join(char_output_dir, "binks"), exist_ok=True); files_found = True
                new_filename = f"{output_name.lower()}_{source_filename.replace('.bikk', '.bik')}"
                shutil.copy2(source_file, os.path.join(char_output_dir, "binks", new_filename))
                copied_files[source_file] = new_filename
            if source_file in copied_files:
                final_mappings[key] = copied_files[source_file]
                
    if final_mappings:
        write_aligned_json(final_mappings, os.path.join(char_output_dir, "binks", "mapping.json"))
        print(f"    └─ Found and processed bink files, created mapping.json")
    return bool(final_mappings)

def create_meta_json(folder_name: str, char_info: dict, cli_args: argparse.Namespace):
    """Creates the final meta.json file based on all processed data."""
    output_dir = os.path.join(OUTPUT_AI_DIR, folder_name)
    
    # Determine the 'name' field based on whether it's a vanilla remake or a new character.
    if not char_info['custom_name']:
        aic_filename_base = os.path.splitext(char_info['aic_file'])[0]
        meta_name = f"{aic_filename_base} {char_info['original_name']}"
    else:
        meta_name = char_info['custom_name']

    meta_data = {
        "name": meta_name,
        "description": "",
        "author": cli_args.author,
        "link": "",
        "version": "1.0.0",
        "defaultLang": cli_args.defaultLang,
        "supportedLang": [cli_args.defaultLang],
        "switched": char_info["status"]
    }
    with open(os.path.join(output_dir, "meta.json"), 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, indent=2)
    print(f"    └─ Successfully created meta.json for '{folder_name}'")

def process_cr_files(aic_files: list, processed_chars: dict):
    """Finds and triggers the processing of all relevant cr.json files."""
    existing_folders = list(processed_chars.keys())
    if len(aic_files) == 1:
        print("\nSingle AIC configuration found. Looking for 'cr.json' in root folder.")
        if os.path.exists('cr.json'):
            succeeded = lines_generator.generate_lines_files('cr.json', existing_folders, OUTPUT_AI_DIR)
            for folder in succeeded:
                if folder in processed_chars: processed_chars[folder]["status"]["lines"] = True
        else: print("Warning: 'cr.json' not found. Skipping lines generation.")
    else:
        print(f"\nMultiple AIC configurations found. Looking for 'cr.json' files in '{CR_INPUT_DIR}'.")
        if not os.path.isdir(CR_INPUT_DIR):
            print(f"Warning: Directory '{CR_INPUT_DIR}' not found. Skipping lines generation.")
            return
        cr_subfolders = [d for d in os.listdir(CR_INPUT_DIR) if os.path.isdir(os.path.join(CR_INPUT_DIR, d))]
        for aic_file in aic_files:
            best_cr_folder = find_best_folder_match(os.path.splitext(aic_file)[0], cr_subfolders)
            if best_cr_folder:
                succeeded = lines_generator.generate_lines_files(os.path.join(CR_INPUT_DIR, best_cr_folder, 'cr.json'), existing_folders, OUTPUT_AI_DIR)
                for folder in succeeded:
                    if folder in processed_chars: processed_chars[folder]["status"]["lines"] = True
            else: print(f"Warning: No matching 'cr' subfolder found for '{aic_file}'.")

def parse_cli_args() -> argparse.Namespace:
    """Sets up and parses command-line arguments."""
    parser = argparse.ArgumentParser(description="A comprehensive converter for Stronghold Crusader AI assets.")
    parser.add_argument('--author', type=str, default="Unknown", help="Set the author name for meta.json files.")
    parser.add_argument('--defaultLang', type=str, default="de", help="Set the default language (e.g., 'en', 'de') for meta.json files.")
    return parser.parse_args()

# --- MAIN ORCHESTRATOR ---
def main(args: argparse.Namespace):
    """Main function to orchestrate the entire generation process."""
    cli_args = parse_cli_args()
    print("Starting AI character file generation script.")
    if not all(os.path.isdir(p) for p in [AIC_INPUT_DIR, TROOPS_INPUT_DIR, AIV_INPUT_DIR]):
        print("FATAL ERROR: Could not find all required UCP input directories. Halting.")
        sys.exit(1)

    troop_data = load_all_troop_data(TROOPS_INPUT_DIR)
    processed_chars = {}
    print(f"\nProcessing AI character files from '{AIC_INPUT_DIR}'...")
    
    # Pre-scan all asset directories once to avoid repeated OS calls in the loop.
    asset_folders = { "aiv": [d for d in os.listdir(AIV_INPUT_DIR) if os.path.isdir(os.path.join(AIV_INPUT_DIR, d))], "portraits": [d for d in os.listdir(PORTRAITS_INPUT_DIR) if os.path.isdir(os.path.join(PORTRAITS_INPUT_DIR, d))] if os.path.isdir(PORTRAITS_INPUT_DIR) else [], "speech": [d for d in os.listdir(SPEECH_INPUT_DIR) if os.path.isdir(os.path.join(SPEECH_INPUT_DIR, d))] if os.path.isdir(SPEECH_INPUT_DIR) else [], "binks": [d for d in os.listdir(BINKS_INPUT_DIR) if os.path.isdir(os.path.join(BINKS_INPUT_DIR, d))] if os.path.isdir(BINKS_INPUT_DIR) else [] }
    aic_files = [f for f in os.listdir(AIC_INPUT_DIR) if f.endswith('.json')]
    is_single_config = len(aic_files) == 1
    
    for filename in aic_files:
        print(f"--- Reading file: {filename} ---")
        aic_filename_base = os.path.splitext(filename)[0]
        
        # Determine all asset source paths for the current AIC file.
        asset_paths = {}
        asset_paths["aiv"] = os.path.join(AIV_INPUT_DIR, find_best_folder_match(aic_filename_base, asset_folders["aiv"])) if find_best_folder_match(aic_filename_base, asset_folders["aiv"]) else None
        if is_single_config:
            asset_paths["portraits"], asset_paths["binks"] = os.path.join("interface_icons2", "Images"), "binks"
            if os.path.isdir("fx/speech"): asset_paths["speech"] = "fx/speech"
            elif os.path.isdir("fx/Speech"): asset_paths["speech"] = "fx/Speech"
            else: asset_paths["speech"] = None
        else:
            asset_paths["portraits"] = os.path.join(PORTRAITS_INPUT_DIR, find_best_folder_match(aic_filename_base, asset_folders["portraits"])) if find_best_folder_match(aic_filename_base, asset_folders["portraits"]) else None
            asset_paths["speech"] = os.path.join(SPEECH_INPUT_DIR, find_best_folder_match(aic_filename_base, asset_folders["speech"])) if find_best_folder_match(aic_filename_base, asset_folders["speech"]) else None
            asset_paths["binks"] = os.path.join(BINKS_INPUT_DIR, find_best_folder_match(aic_filename_base, asset_folders["binks"])) if find_best_folder_match(aic_filename_base, asset_folders["binks"]) else None

        print(f"  ├─ Matched AIV folder: '{os.path.basename(asset_paths['aiv'])}'" if asset_paths['aiv'] else "  ├─ No matching AIV folder found.")
        print(f"  ├─ Using Portrait path: '{asset_paths['portraits']}'")
        print(f"  ├─ Using Speech path: '{asset_paths['speech']}'")
        print(f"  ├─ Using Binks path: '{asset_paths['binks']}'")

        with open(os.path.join(AIC_INPUT_DIR, filename), 'r', encoding='utf-8-sig') as f:
            for character in json.load(f).get("AICharacters", []):
                original_name = character.get("Name")
                if not original_name: continue
                folder_name = sanitize_name(character.get("CustomName") or original_name)
                if folder_name in processed_chars:
                    print(f"\nFATAL ERROR: Duplicate AI name '{folder_name}' detected. Halting.")
                    sys.exit(1)
                
                output_dir = os.path.join(OUTPUT_AI_DIR, folder_name)
                os.makedirs(output_dir, exist_ok=True)
                
                matched_troops = troop_data.get(original_name, {})
                lord_data, start_troops_data = matched_troops.get("Lord", {}), {"normal": dict(zip(matched_troops.get("normal", {}).get('Units', []), matched_troops.get("normal", {}).get('Counts', []))), "crusader": dict(zip(matched_troops.get("crusader", {}).get('Units', []), matched_troops.get("crusader", {}).get('Counts', []))), "deathmatch": dict(zip(matched_troops.get("deathmatch", {}).get('Units', []), matched_troops.get("deathmatch", {}).get('Counts', [])))}
                with open(os.path.join(output_dir, "character.json"), 'w', encoding='utf-8') as char_f:
                    json.dump({"lord": lord_data, "startTroops": start_troops_data, "aic": character.get("Personality", {})}, char_f, indent=2, ensure_ascii=False)
                print(f"  Successfully created: {os.path.join(output_dir, 'character.json')}")

                processed_chars[folder_name] = {
                    "original_name": original_name,
                    "custom_name": character.get("CustomName", ""),
                    "aic_file": filename,
                    "status": {
                        "aic": bool(character.get("Personality")), "lord": bool(lord_data), "startTroops": any(start_troops_data.values()),
                        "aiv": process_aiv_files(original_name, folder_name, output_dir, asset_paths["aiv"]),
                        "portrait": process_portrait_files(original_name, output_dir, asset_paths["portraits"]),
                        "speech": process_speech_files(original_name, folder_name, output_dir, asset_paths["speech"]),
                        "binks": process_binks_files(original_name, folder_name, output_dir, asset_paths["binks"]),
                        "lines": False
                    }
                }
    
    process_cr_files(aic_files, processed_chars)

    print("\n--- Creating meta.json files ---")
    for folder_name, char_info in processed_chars.items():
        create_meta_json(folder_name, char_info, cli_args)

    print(f"\nProcessing complete. All files have been generated in '{OUTPUT_AI_DIR}'.")

if __name__ == "__main__":
    main(parse_cli_args())