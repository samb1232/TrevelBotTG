class Text:
    __name__ = "TEXT"

    def __init__(self, text: str):
        self.text = text


class Picture:
    __name__ = "PICTURE"

    def __init__(self, picture_source: str):
        self.picture_source = picture_source


class Audio:
    __name__ = "AUDIO"

    def __init__(self, audio_source: str):
        self.audio_source = audio_source


class Waypoint:
    def __init__(self, components: list, buttons_names: list, quiz_answer: str | None = None):
        # Check if Waypoint is empty
        if len(components) == 0 or len(buttons_names) == 0:
            raise ValueError("Error. An empty waypoint or waypoint without buttons_names cannot be created.")
        self.components = components.copy()
        self.buttons_names = buttons_names.copy()
        self.quiz_answer = quiz_answer
