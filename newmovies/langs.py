_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese",
    "cn": "Chinese", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "ml": "Malayalam",
    "kn": "Kannada", "bn": "Bengali", "mr": "Marathi", "pa": "Punjabi", "ur": "Urdu",
    "nl": "Dutch", "sv": "Swedish", "no": "Norwegian", "nb": "Norwegian", "da": "Danish",
    "fi": "Finnish", "pl": "Polish", "tr": "Turkish", "th": "Thai", "id": "Indonesian",
    "ar": "Arabic", "he": "Hebrew", "fa": "Persian", "uk": "Ukrainian", "cs": "Czech",
    "hu": "Hungarian", "ro": "Romanian", "el": "Greek", "vi": "Vietnamese", "tl": "Tagalog",
    "ms": "Malay", "is": "Icelandic", "sr": "Serbian", "hr": "Croatian", "sk": "Slovak",
    "bg": "Bulgarian", "ca": "Catalan", "et": "Estonian", "lv": "Latvian", "lt": "Lithuanian",
    "sl": "Slovenian", "gl": "Galician", "eu": "Basque", "af": "Afrikaans", "sw": "Swahili",
    "nn": "Norwegian", "fil": "Filipino",
}


def name(code):
    if not code:
        return None
    return _NAMES.get(code, code.upper())
