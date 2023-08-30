import logging

from database.tables.excursion_test import Excursion_test
from excursion import Excursion
from waypoint import Waypoint, Text, Audio, Picture

logger = logging.getLogger(__name__)

excursion_test = Excursion(description_text=
                           ("Кто и зачем прорыл подземные ходы под Летним садом, "
                            "какой смысл хотел заложить Петр I в строительство сада, как проходили смотры невест,"
                            "первые признаки феминизма и почему никто не ехал в Петербург? \n"
                            "Ответы на все эти вопросы можно найти прогуливаясь по самой известной зеленой зоне города,"
                            "если знать где и что искать. Сегодня предлагаем раскрыть тайны этого места.\n"
                            "Если решишь приостановить экскурсию, введи команду /stop!"),
                           finale_message_text="Благодарю за это удивительное приключение! Экскурсия окончена. Ещё "
                                               "увидимся!",
                           description_image_src="Excursion1/map.jpg",
                           waypoints_array=[
                               Waypoint(components=[
                                   Text(
                                       "Первый этап экскурсии. Подходите к точке 1 на карте. Как будете на месте, "
                                       "смело нажимайте кнопку"
                                       "\"На месте\" "),
                                   Picture("Excursion1/point1.png"),
                                   Audio("Excursion1/T1.m4a")
                               ],
                                   buttons_names=["На месте"]
                               ),

                               Waypoint(components=[
                                   Text("Оглянитесь вокруг и найдите лицо героини греческих мифов. Что это за женщина?")
                               ],
                                   buttons_names=["Афродита", "Сирена", "Медуза Горгона", "Фемида"],
                                   quiz_answer="Медуза Горгона"
                               ),
                               Waypoint([
                                   Text("Второй этап экскурсии"),
                                   Audio("Excursion1/T2.m4a")
                               ],
                                   buttons_names=["Дальше"]
                               ),
                               Waypoint(components=[
                                   Text("Третий этап экскурсии"),
                                   Audio("Excursion1/T3.m4a")
                               ],
                                   buttons_names=["Поехали!"]
                               ),

                               Waypoint(components=[
                                   Text("Приехали")
                               ],
                                   buttons_names=["Спасибо за экскурсию!"]
                               )],
                           excursion_db_class=Excursion_test)
