"""
Configuration Manager - Advanced Screen Reader
FileName: config.py
Description: Manages global configuration parameters, offline engine paths, 
             hotkeys, and persistent load/save settings via JSON.
"""

import os
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any

logger = logging.getLogger("ScreenReader")


@dataclass
class Config:
    # --- App Info ---
    APP_NAME: str = "Advanced Screen Reader"
    VERSION: str = "1.0.0"
    DEBUG_MODE: bool = False

    # --- Text-To-Speech (TTS) Settings ---
    TTS_ENGINE: str = "pyttsx3"  # Default offline TTS engine
    TTS_RATE: int = 200          # Words per minute
    TTS_VOLUME: float = 1.0      # Range: 0.0 to 1.0
    TTS_VOICE_INDEX: int = 0     # Default Windows SAPI5 voice index

    # --- Speech-To-Text (STT / Voice Commands) Settings ---
    STT_ENGINE: str = "vosk"     # Offline Vosk or local Whisper
    VOSK_MODEL_PATH: str = "models/vosk-model-small-en-us"
    WHISPER_MODEL_SIZE: str = "tiny"

    # --- OCR Settings (Offline Document Reader) ---
    TESSERACT_PATH: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_LANGUAGE: str = "eng"

    # --- AI Vision Settings (Offline Image Captioning) ---
    VISION_MODEL_NAME: str = "Salesforce/blip-image-captioning-base"
    ENABLE_AI_VISION: bool = True

    # --- Global Hotkeys ---
    HOTKEYS: Dict[str, str] = field(default_factory=lambda: {
        "read_screen": "<ctrl>+<alt>+r",
        "read_selection": "<ctrl>+<alt>+s",
        "stop_speech": "<ctrl>",
        "ocr_screen": "<ctrl>+<alt>+o",
        "describe_image": "<ctrl>+<alt>+i",
        "toggle_voice_command": "<ctrl>+<alt>+v"
    })

    # --- File Paths ---
    BASE_DIR: str = field(default_factory=lambda: os.path.dirname(os.path.abspath(__file__)))
    CONFIG_FILE_NAME: str = "config.json"

    @property
    def config_file_path(self) -> str:
        """Returns full absolute path to config.json."""
        return os.path.join(self.BASE_DIR, self.CONFIG_FILE_NAME)

    def save_to_file(self) -> bool:
        """Saves current configuration to local JSON file."""
        try:
            data = asdict(self)
            with open(self.config_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Configuration saved successfully to {self.config_file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False

    @classmethod
    def load_from_file(cls) -> "Config":
        """Loads configuration from JSON file. Returns default config if missing or invalid."""
        default_config = cls()
        target_path = default_config.config_file_path

        if not os.path.exists(target_path):
            logger.info("Config file not found. Generating default config.json...")
            default_config.save_to_file()
            return default_config

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Configuration loaded successfully from JSON file.")
            
            # Merge loaded dict into class
            config = cls()
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            return config
        except Exception as e:
            logger.error(f"Error reading config file: {str(e)}. Falling back to defaults.")
            return default_config


# Global Config instance for easy importing across modules
config_instance = Config.load_from_file()


if __name__ == "__main__":
    # Test Module Standalone Execution
    print(f"Loaded App: {config_instance.APP_NAME} v{config_instance.VERSION}")
    print(f"TTS Speech Rate: {config_instance.TTS_RATE}")
    print(f"Tesseract Path: {config_instance.TESSERACT_PATH}")
    
    # Save a copy to verify JSON file generation
    config_instance.save_to_file()
