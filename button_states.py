class MenuButtonStates:
    MAIN_MENU = "main_menu"
    CHOOSE_EXCURSION = "choose_excursion"
    ADDITIONAL_INFORMATION = "additional_information"
    TARIFFS = "tariffs"
    NONE = "_"


class ExcursionButtonStates:
    MAIN_MENU = "main_menu"
    CHOOSE_EXCURSION = "choose_excursion"
    BEGIN_EXCURSION = "begin_excursion"


class ConversationStates:
    MAIN_MENU: int = 0
    TARIFF_PAYMENT: int = 1
    EXCURSION: int = 2
    TEST_EXCURSION: int = 3
