# character.py

class Character:
    def __init__(self, name, gender, race, char_class):
        self.name = name
        self.gender = gender
        self.race = race
        self.char_class = char_class
        # Можно добавить дополнительные параметры, такие как уровень и опыт
        self.level = 1
        self.experience = 0

    def get_info(self):
        # Функция для отображения информации о персонаже
        return (f"Name: {self.name}\n"
                f"Gender: {self.gender}\n"
                f"Race: {self.race}\n"
                f"Class: {self.char_class}\n"
                f"Level: {self.level}\n"
                f"Experience: {self.experience}")
