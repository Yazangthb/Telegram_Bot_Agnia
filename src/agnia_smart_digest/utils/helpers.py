def prepare_prompt(prompt, user_request):
    return prompt.replace("{USER_REQUEST}", user_request)


def strip_url(url: str) -> str:
    return url.rstrip("/")
