from vkbottle import BaseStateGroup

class NewaccountState(BaseStateGroup):
    INLOGIN = 1
    INSCHOOL = 2

class ImportState(BaseStateGroup):
    INTOKEN = 3

class MenuState(BaseStateGroup):
    RASP = 1
    DZ = 2
    DELETE = 3