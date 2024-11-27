import sys
import time
from colorama import init, Fore
init(autoreset=True)


def read_configuration(file):
    """функция считывания конфигурации из файла"""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')

        rotor_set = []
        reflector_set = ""
        for line in lines:
            if line.startswith("rotor"):
                rotor_set.append(line.split(" = ")[1])
            elif line.startswith("reflector"):
                reflector_set = line.split(" = ")[1]

        return rotor_set, reflector_set

    except FileNotFoundError:
        print(Fore.RED + f"Ошибка: файл '{file}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"Ошибка при загрузке конфигурации: {e}")
        sys.exit(1)

class Panel:
    """класс реализующий соединительную панель"""
    def __init__(self, set):
        """
        инициализация соединительной панели
        set - для настроек панели в формате 'БВ'
        """
        self.mapping = {}
        if len(set) % 2 != 0:
            print(Fore.RED + "Ошибка: соединительная панель должна содержать четное количество символов.")
            sys.exit(1)

        for i in range(0, len(set), 2):
            a, b = set[i], set[i + 1]
            self.mapping[a] = b
            self.mapping[b] = a

    def swap(self, char):
        """обработка буквы через соед.панель"""
        return self.mapping.get(char, char)


class Rotor:
    """класс реализующий ротор машины «Энигма»"""
    def __init__(self, set):
        """
        инициализация ротора
        set - для начальной настроек ротора в формате 'АБВГ-ГАБВ'
        """
        try:
            self.alphabet, self.mapping = set.split("-")
            if len(self.alphabet) != len(self.mapping):
                raise ValueError("Алфавит и отображение ротора должны быть одинаковой длины.")
        except ValueError as e:
            print(f"Ошибка в настройке ротора: {e}")
            sys.exit(1)
        self.position = 0

    def turn(self):
        """реализация единичного поворота"""
        self.mapping = self.mapping[1:] + self.mapping[0]
        self.position = (self.position + 1) % len(self.alphabet)

    def forward(self, char):
        """обработка буквы при прямом сигнале"""
        index = self.alphabet.index(char)
        return self.mapping[index]

    def backward(self, char):
        """обработка буквы при обратном сигнале"""
        index = self.mapping.index(char)
        return self.alphabet[index]


class Reflector:
    """класс реализующий рефлектор машины «Энигма»"""
    def __init__(self, set):
        """
        инициализация рефлектора
        set - для настроек рефлектора в формате 'А-Г,Б-В,В-Б,Г-А'
        """
        try:
            self.mapping = dict(pair.split("-") for pair in set.split(","))
        except ValueError:
            print(Fore.RED + "Ошибка в настройке рефлектора. Неверный формат.")
            sys.exit(1)

    def reflect(self, char):
        """обработка буквы при прохождении через рефлектор"""
        return self.mapping[char]


class Enigma:
    """класс реализующий машину «Энигма»"""
    def __init__(self, rotor_set, reflector_set, panel_set, initial_set):
        """
        инициализация машины
        rotor_set - список для строк с настройками роторов
        reflector_set - для настроей рефлектора
        plugboard_set - для настроек соединительной панели
        initial_set - для стартовых позиций роторов в формате 'ААА'
        """
        self.rotors = [Rotor(wiring) for wiring in rotor_set]
        self.reflector = Reflector(reflector_set)
        self.panel = Panel(panel_set)

        if len(initial_positions) != len(self.rotors):
            print(Fore.RED + "Ошибка: количество начальных позиций не соответствует количеству роторов.")
            sys.exit(1)


        # старторые позиции роторов
        for rotor, position in zip(self.rotors, initial_set):
            if position not in rotor.alphabet:
                print(Fore.RED + f"Ошибка: начальная позиция '{position}' недопустима. Доступные буквы: {rotor.alphabet}.")
                sys.exit(1)

            while rotor.alphabet[0] != position:
                rotor.turn()

    def encryption_letter(self, char):
        """шифрование буквы"""
        if char not in self.rotors[0].alphabet:
            print(Fore.RED + f"Ошибка: символ '{char}' не найден в алфавите.")
            sys.exit(1)

        # обработка соединительной панелью
        char = self.panel.swap(char)

        # обработка роторами
        for rotor in self.rotors:
            char = rotor.forward(char)

        # обработка рефлектором
        char = self.reflector.reflect(char)

        # обработка роторами (реверс)
        for rotor in reversed(self.rotors):
            char = rotor.backward(char)

        # обработка соединительной панелью
        char = self.panel.swap(char)

        # поворот ротора
        for i, rotor in enumerate(self.rotors):
            rotor.turn()
            if rotor.position != 0:
                break

        return char

    def encryption_text(self, text):
        """шифрование текста"""
        return ''.join(self.encryption_letter(char) for char in text)


config_file = "enigma_config.txt"
rotor_set, reflector_set = read_configuration(config_file)

initial_positions = input("Введите начальные позиции роторов (например, ААА): ").strip()
panel_set = input("Введите соединительную панель (например, БВ): ").strip()
text = input("Введите текст: ").strip()
if not text:
    print(Fore.RED + "Ошибка: текст не может быть пустым.")
    sys.exit(1)

machine = Enigma(rotor_set, reflector_set, panel_set, initial_positions)
result = machine.encryption_text(text)

print(Fore.YELLOW + f"Идет шифрование...")
time.sleep(1)
print(Fore.GREEN + f"Текст '{text}' успешно зашифрован!")
print(Fore.CYAN + f"Результат: '{result}'")
