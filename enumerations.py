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
    TEST_EXCURSION_1: int = 1
    TEST_EXCURSION_2: int = 2


class Excursion_names:
    TEST_EXCURSION_1: str = "test_excursion_1"
    TEST_EXCURSION_2: str = "test_excursion_2"
