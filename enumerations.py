class MenuCallbackButtons:
    MAIN_MENU = "main_menu"
    CHOOSE_EXCURSION = "choose_excursion"
    ADDITIONAL_INFORMATION = "additional_information"
    TARIFFS = "tariffs"
    GET_STATUS = "get_status"
    NOT_IMPLEMENTED = "_"


class ExcursionCallbackButtons:
    MAIN_MENU = "main_menu"
    CHOOSE_EXCURSION = "choose_excursion"
    BEGIN_EXCURSION = "begin_excursion"


class ConversationStates:
    MAIN_MENU: int = 0
    TEST_EXCURSION: int = 1
