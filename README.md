# UCP2 to UCP3 AI Character Asset Converter

This tool is a suite of Python scripts designed to convert and package AI character assets from Stronghold Crusader modding resources into a structured, game-ready format. It automatically handles AIC settings, troops, AIV castles, portraits, speech, binks, and text lines, creating a clean output folder for each AI character.

## Prerequisites

Before running the script, please ensure you have the following:

1.  **Python Installed:** Python 3.7 or newer is required.
2.  **Python in PATH:** During installation, make sure you checked the option "Add Python to PATH". You can verify this by opening a terminal and typing `python --version` or `python3 --version`. If you see a version number, you are ready.

## Folder & File Setup

For the scripts to work correctly, your files must be organized in a specific structure. Create a main project folder (e.g., `UCP_Converter`) and place all files and folders inside it as shown below.

### 1. Script Files

Place the three Python scripts directly inside your main project folder:
- `create_character_ucp3.py` (the main script)
- `lines_generator.py` (the module for processing text lines)
- `shared_utils.py` (the module for shared functions)

### 2. Input Data Structure

Your input data must be organized inside a `UCP` folder. The script also looks for some folders in the root directory if you are only processing a single configuration.

```
/Your-Project-Folder/
│
├── create_character_ucp3.py
├── lines_generator.py
├── shared_utils.py
│
├─- UCP/
│   └─- resources/
│       ├─- aic/
│       │   └─- (your .json AIC files)
│       ├─- aiv/
│       │   └─- (your AIV castle folders)
│       ├─- binks/
│       │   └─- (your .bik video folders - for multi-AIC setup)
│       ├─- cr/
│       │   └─- (your cr.json folders - for multi-AIC setup)
│       ├─- portraits/
│       │   └─- (your portrait folders - for multi-AIC setup)
│       ├─- speech/
│       │   └─- (your speech .wav folders - for multi-AIC setup)
│       └─- troops/
│           └─- (your .json troops files)
│
└─- (Optional folders for a SINGLE AIC file setup)
    ├─- cr.json
    ├─- binks/
    │   └─- (your .bik video files)
    ├─- fx/
    │   └─- speech/ or Speech/
    │       └─- (your .wav speech files)
    └─- interface_icons2/
        └─- Images/
            └─- (your .png portrait files)
```

**Note:** The script automatically detects if you are processing a single AIC configuration or multiple. If only **one** `.json` file is found in `UCP/resources/aic/`, it will look for assets in the optional root folders (`cr.json`, `binks/`, etc.). If multiple AIC files are found, it will look for corresponding asset folders inside `UCP/resources/`.

## How to Run the Script

The easiest way to run the script is using the integrated terminal in a code editor like VS Code.

1.  Open your main project folder (`Your-Project-Folder`) in Visual Studio Code.
2.  Open the built-in terminal (Shortcut: `Ctrl+` \` or from the top menu: `Terminal > New Terminal`).
3.  In the terminal prompt, type the command to run the script, including any arguments you want to use.

### Example Command

This is a complete example of how to run the script, setting the author and default language for the output `meta.json` files.

```bash
python create_character_ucp3.py --author="Your Name" --defaultLang="en"
```

### Command-Line Arguments

The script accepts the following optional arguments:

-   `--author="<name>"`
    -   Sets the author name in the generated `meta.json` files.
    -   If not provided, it defaults to `"Unknown"`.

-   `--defaultLang="<lang_code>"`
    -   Sets the default language (e.g., "en", "de") in the `meta.json` files.
    -   If not provided, it defaults to `"de"`.
