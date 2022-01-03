def remove_usernames(text: str) -> str:
    usernames = [word for word in text.split() if word.startswith("@")]
    for username in usernames:
        text = text.replace(username, "...")
    return text
