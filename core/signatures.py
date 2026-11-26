# Supported file formats and their valid extensions

EXTENSION_MAP = {
    "jpg": {"jpg", "jpeg", "jpe"},
    "png": {"png"},
    "gif": {"gif"},
    "pdf": {"pdf"},
    "exe": {"exe", "dll", "scr"},
    "zip": {"zip"},
    "rar": {"rar"},
    "7z": {"7z"},
    "mp3": {"mp3"},
    "mp4": {"mp4", "m4v"},
    "wav": {"wav"},
    "bmp": {"bmp"},
    "webp": {"webp"},
    "tif": {"tif", "tiff"},
    "docx": {"docx"},
    "xlsx": {"xlsx"},
    "pptx": {"pptx"},
}

# Potentially dangerous extensions

DANGEROUS_EXTENSIONS = {
    "exe", "bat", "cmd", "scr",
    "msi", "dll", "ps1", "vbs",
    "js", "com", "hta", "lnk"
}

# Common extensions used to disguise files

DECOY_EXTENSIONS = {
    "pdf", "jpg", "jpeg", "png",
    "gif", "txt", "doc", "docx",
    "xls", "xlsx", "pptx", "mp4"
}

# Unicode characters associated with filename manipulation

SUSPICIOUS_UNICODE = {
    "\u202a", "\u202b", "\u202c",
    "\u202d", "\u202e", "\u200b",
    "\u200c", "\u200d", "\u2066",
    "\u2067", "\u2068", "\u2069",
    "\ufeff"
}
