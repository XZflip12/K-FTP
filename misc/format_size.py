def format_size(size_bytes):
    if size_bytes is None or size_bytes == "-":
        return ""
    try:
        size = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except ValueError:
        return ""
