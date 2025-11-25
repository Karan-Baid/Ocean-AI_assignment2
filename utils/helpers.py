def shorten_text(text, max_len=50):
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def get_category_color(category):
    colors = {
        "Important": "#ff4444",
        "To-Do": "#ff9800",
        "Meeting Request": "#2196f3",
        "Project Update": "#4caf50",
        "Newsletter": "#9c27b0",
        "Spam": "#757575",
        "Personal": "#00bcd4"
    }
    return colors.get(category, "#999999")
