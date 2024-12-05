import argparse
import sys
import time
from colorama import init, Fore

init(autoreset=True)


def read_configuration(file):
    """Функция считывания конфигурации из файла"""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')

        rotor_set = []
        reflector_set = ""
        for line in lines:
            line = line.replace(" ", "")
            if line.startswith("rotor"):
                rotor_set.append(line.split("=")[1])
            elif line.startswith("reflector"):
                reflector_set = line.split("=")[1]

        return rotor_set, reflector_set
    except FileNotFoundError:
        raise FileNotFoundError(f"Ошибка: файл '{file}' не найден.")
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке конфигурации: {e}")


class Panel:
    """Класс реализующий соединительную панель"""
    def __init__(self, set, alphabet):
        """
        Инициализация соединительной панели
        set - настройки панели в формате 'БВ'
        alphabet - алфавит
        """
        self.mapping = {}
        if len(set) % 2 != 0:
            raise ValueError("Соединительная панель должна содержать чётное количество символов.")

        for i in range(0, len(set), 2):
            a, b = set[i], set[i + 1]
            if a not in alphabet or b not in alphabet:
                raise ValueError(f"Символы '{a}' или '{b}' отсутствуют в алфавите '{alphabet}'.")

            self.mapping[a] = b
            self.mapping[b] = a

    def swap(self, char):
        return self.mapping.get(char, char)


class Rotor:
    """Класс реализующий ротор машины «Энигма»"""
    def __init__(self, set):
        """
        Инициализация ротора
        set - настройки ротора в формате 'АБВГ-ГАБВ'
        """
        try:
            self.alphabet, self.mapping = set.split("-")
            if len(self.alphabet) != len(self.mapping):
                raise ValueError("Алфавит и отображение ротора должны быть одинаковой длины.")
            seen = {}
            for char in self.mapping:
                if char in seen:
                    raise ValueError(
                        f"Ошибка в настройке ротора: символ '{char}' повторяется в отображении '{self.mapping}'.")
                seen[char] = True
        except ValueError as e:
            raise ValueError(f"Ошибка в настройке ротора: {e}")
        self.position = 0

    def turn(self):
        """Реализация единичного поворота"""
        self.mapping = self.mapping[1:] + self.mapping[0]
        self.position = (self.position + 1) % len(self.alphabet)

    def set_position(self, char):
        """Установка ротора в заданную позицию"""
        if char not in self.alphabet:
            raise ValueError(f"Символ '{char}' отсутствует в алфавите ротора.")
        steps = self.alphabet.index(char)
        self.mapping = self.mapping[steps:] + self.mapping[:steps]

    def forward(self, char):
        """Обработка буквы при прямом сигнале"""
        index = self.alphabet.index(char)
        return self.mapping[index]

    def backward(self, char):
        """Обработка буквы при обратном сигнале"""
        index = self.mapping.index(char)
        return self.alphabet[index]


class Reflector:
    """Класс реализующий рефлектор машины «Энигма»"""
    def __init__(self, set):
        """
        Инициализация рефлектора
        set - настройки рефлектора в формате 'А-Г,Б-В,Г-А,В-Б'
        """
        try:
            self.mapping = dict(pair.split("-") for pair in set.split(","))
        except ValueError:
            raise ValueError("Ошибка в настройке рефлектора. Неверный формат.")

        # Проверка на симметричность отображения
        for a, b in self.mapping.items():
            if b not in self.mapping or self.mapping[b] != a:
                raise ValueError(f"Рефлектор должен быть симметричным: отсутствует пара '{b}-{a}' для '{a}-{b}'.")

    def reflect(self, char):
        """Обработка буквы при прохождении через рефлектор"""
        try:
            return self.mapping[char]
        except KeyError:
            raise KeyError(f"Ошибка рефлектора: символ '{char}' не имеет соответствия.")


class Enigma:
    """Класс реализующий машину «Энигма»"""
    def __init__(self, rotor_set, reflector_set, panel_set, initial_set):
        """
        Инициализация машины
        rotor_set - список строк с настройками роторов
        reflector_set - настройки рефлектора
        plugboard_set - настройки соединительной панели
        initial_set - стартовые позиции роторов в формате 'ААА'
        """
        self.rotors = [Rotor(wiring) for wiring in rotor_set]
        self.reflector = Reflector(reflector_set)
        self.panel = Panel(panel_set, self.rotors[0].alphabet)

        if len(initial_set) != len(self.rotors):
            raise ValueError("Количество начальных позиций не соответствует количеству роторов.")

        # Установка стартовых позиций роторов
        for rotor, position in zip(self.rotors, initial_set):
            rotor.set_position(position)

    def encryption_letter(self, char):
        """Шифрование буквы"""
        if char not in self.rotors[0].alphabet:
            raise ValueError(f"Символ '{char}' не найден в алфавите.")

        # Обработка соединительной панелью
        char = self.panel.swap(char)

        # Обработка роторами
        for rotor in self.rotors:
            char = rotor.forward(char)

        # Обработка рефлектором
        char = self.reflector.reflect(char)

        # Обработка роторами (реверс)
        for rotor in reversed(self.rotors):
            char = rotor.backward(char)

        # Обработка соединительной панелью
        char = self.panel.swap(char)

        # Поворот роторов
        for rotor in self.rotors:
            rotor.turn()
            if rotor.position != 0:
                break

        return char

    def encryption_text(self, text):
        """Шифрование текста"""
        return ''.join(self.encryption_letter(char) for char in text)


# Основной блок
parser = argparse.ArgumentParser(description="Шифровальная машина Энигма.")
parser.add_argument("-c", "--config", help="Путь к файлу конфигурации (например, enigma_config.txt)")
parser.add_argument("-i", "--initial", help="Начальные позиции роторов (например, АБВ)")
parser.add_argument("-p", "--panel", help="Настройки соединительной панели (например, БВГД)")
parser.add_argument("-t", "--text", help="Текст для шифрования")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.config and args.initial and args.panel and args.text:
        config_file = args.config
        initial_positions = args.initial.strip()
        panel_set = args.panel.strip()
        text = args.text.strip()
    else:
        config_file = input("Введите путь к файлу конфигурации (например, enigma_config.txt): ").strip()
        initial_positions = input("Введите начальные позиции роторов (например, АБВ): ").strip()
        panel_set = input("Введите соединительную панель (например, БВГД): ").strip()
        text = input("Введите текст для шифрования: ").strip()
        if not text:
            print(Fore.RED + "Ошибка: текст не может быть пустым.")
            sys.exit(1)

    rotor_set, reflector_set = read_configuration(config_file)

    try:
        machine = Enigma(rotor_set, reflector_set, panel_set, initial_positions)
    except Exception as e:
        print(Fore.RED + f"Ошибка инициализации машины: {e}")
        sys.exit(1)

    result = machine.encryption_text(text)

    print(Fore.YELLOW + f"Идет шифрование...")
    time.sleep(1)
    print(Fore.GREEN + f"Текст '{text}' успешно зашифрован!")
    print(Fore.CYAN + f"Результат: '{result}'")
