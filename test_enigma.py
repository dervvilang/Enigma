import pytest
from enigma import Enigma, Rotor, Reflector, Panel, read_configuration


# фикстура для создания машины Энигма с заданной конфигурацией
@pytest.fixture
def enigma_machine():
    rotor_set = ['АБВГ-ГАБВ', 'АБВГ-БАГВ', 'АБВГ-ВГАБ']
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'
    panel_set = 'БВ'
    initial_positions = 'ААА'
    return Enigma(rotor_set, reflector_set, panel_set, initial_positions)


# тест на корректность шифрования и дешифрования с одинаковыми настройками
@pytest.mark.parametrize("input_text, expected_output", [
    ("АБ", "ВВ"),
    ("ААА", "ВГВ"),
    ("ГАВ", "БГА")
])
def test_encrypt_decrypt(enigma_machine, input_text, expected_output):
    encrypted_text = enigma_machine.encryption_text(input_text)
    assert encrypted_text == expected_output


# тест на то, что разные начальные позиции приводят к разным результатам
def test_different_initial_positions():
    rotor_set = ['АБВГ-ГАБВ', 'АБВГ-БАГВ', 'АБВГ-ВГАБ']
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'
    panel_set = 'БВ'

    enigma1 = Enigma(rotor_set, reflector_set, panel_set, 'ААА')
    enigma2 = Enigma(rotor_set, reflector_set, panel_set, 'АБВ')

    input_text = 'ААА'
    assert enigma1.encryption_text(input_text) != enigma2.encryption_text(input_text)


# тест на некорректные стартовые позиции роторов
def test_invalid_initial_positions():
    rotor_set = ['АБВГ-ГАБВ', 'АБВГ-БАГВ', 'АБВГ-ВГАБ']
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'
    panel_set = 'БВ'

    with pytest.raises(ValueError):
        Enigma(rotor_set, reflector_set, panel_set, 'XYZ')


# тест на обработку некорректного ввода соединительной панели
def test_invalid_panel():
    rotor_set = ['АБВГ-ГАБВ', 'АБВГ-БАГВ', 'АБВГ-ВГАБ']
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'

    with pytest.raises(ValueError):
        Enigma(rotor_set, reflector_set, 'Б', 'ААА')


# тест на исключение при неверном символе в тексте для шифрования
def test_invalid_character_in_text(enigma_machine):
    with pytest.raises(ValueError):
        enigma_machine.encryption_text('Z1!А')


# тесты на работу с разными сообщениями
@pytest.mark.parametrize("input_text", ["А", "БАБ", "ГВГ", "ААББГГ"])
def test_various_messages(enigma_machine, input_text):
    encrypted = enigma_machine.encryption_text(input_text)
    assert isinstance(encrypted, str) and len(encrypted) == len(input_text)

# тест с рефлектором
def test_reflector():
    reflector = Reflector('А-Г,Б-В,В-Б,Г-А')
    assert reflector.reflect('А') == 'Г'
    assert reflector.reflect('Б') == 'В'


# тест на некорректную дешифровку при замене ротора
def test_incorrect_rotor_replacement():
    rotor_set1 = ['АБВГ-ГАБВ', 'АБВГ-БАГВ', 'АБВГ-ВГАБ']
    rotor_set2 = ['АБВГ-ВБАГ', 'АБВГ-БАГВ', 'АБВГ-ГАБВ']
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'
    panel_set = 'БВ'

    enigma1 = Enigma(rotor_set1, reflector_set, panel_set, 'ААА')
    input_text = 'АБВ'
    encrypted_text = enigma1.encryption_text(input_text)

    enigma2 = Enigma(rotor_set2, reflector_set, panel_set, 'ААА')
    decrypted_text = enigma2.encryption_text(encrypted_text)

    assert decrypted_text != input_text

# тест на правильную конфигурацию рефлектора
def test_valid_reflector_configuration():
    valid_reflector_set = 'А-Г,Б-В,Г-А,В-Б'
    reflector = Reflector(valid_reflector_set)
    assert reflector.mapping == {'А': 'Г', 'Б': 'В', 'Г': 'А', 'В': 'Б'}


# тест на некорректную конфигурацию рефлектора с нарушенной симметрией
def test_invalid_reflector_configuration():
    invalid_reflector_set = 'А-Г,Б-В,Г-Б,В-А'
    with pytest.raises(ValueError, match="Рефлектор должен быть симметричным: отсутствует пара 'Г-А' для 'А-Г'."):
        Reflector(invalid_reflector_set)


# тест на обработку отсутствующего символа в рефлекторе
def test_reflector_key_error():
    valid_reflector_set = 'А-Г,Б-В,Г-А,В-Б'
    reflector = Reflector(valid_reflector_set)

    with pytest.raises(KeyError, match="Ошибка рефлектора: символ 'Д' не имеет соответствия."):
        reflector.reflect('Д')


# тест на некорректную конфигурацию ротора с повторяющимися символами
def test_invalid_rotor_repeated_symbols():
    invalid_rotor_set = 'АБВГ-ГАБА'
    with pytest.raises(ValueError, match="Ошибка в настройке ротора: символ 'А' повторяется в отображении 'ГАБА'."):
        Rotor(invalid_rotor_set)


# тест на некорректную конфигурацию ротора с разной длиной алфавита и отображения
def test_invalid_rotor_length_mismatch():
    invalid_rotor_set = 'АБВГ-ГАБ'
    with pytest.raises(ValueError, match="Алфавит и отображение ротора должны быть одинаковой длины."):
        Rotor(invalid_rotor_set)


# тест на read_configuration с несуществующим файлом
def test_read_configuration_file_not_found():
    with pytest.raises(FileNotFoundError, match="Ошибка: файл 'nonexistent.txt' не найден."):
        read_configuration('nonexistent.txt')


# тест read_configuration с некорректным форматом
def test_read_configuration_invalid_format(tmp_path):
    config_file = tmp_path / "bad_config.txt"
    # Конфигурация, не содержащая разделителей "="
    config_file.write_text("rotor_1 : АБВГ-ГАБВ", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Ошибка при загрузке конфигурации:.*"):
        read_configuration(config_file)


# Тест для обработки некорректного символа в панели
def test_invalid_panel_symbols():
    with pytest.raises(ValueError, match="Символы 'X' или 'Y' отсутствуют в алфавите.*"):
        Panel("XY", "АБВГ")


def test_panel_odd_length():
    with pytest.raises(ValueError, match="Соединительная панель должна содержать чётное количество символов."):
        Panel("ABC", "АБВГ")


def test_rotor_invalid_position():
    rotor = Rotor("АБВГ-ГАБВ")
    with pytest.raises(ValueError, match="Символ 'X' отсутствует в алфавите ротора."):
        rotor.set_position("X")


def test_reflector_missing_symbol():
    reflector = Reflector("А-Г,Б-В,Г-А,В-Б")
    with pytest.raises(KeyError, match="Ошибка рефлектора: символ 'Д' не имеет соответствия."):
        reflector.reflect("Д")


def test_rotor_turn():
    rotor = Rotor("АБВГ-ГАБВ")
    original_mapping = rotor.mapping
    rotor.turn()
    assert rotor.mapping == original_mapping[1:] + original_mapping[:1]
    assert rotor.position == 1


def test_reflector_invalid_format():
    invalid_reflector_set = "А-Г;Б-В;Г-А;В-Б"  # Используем некорректный разделитель
    with pytest.raises(ValueError, match="Ошибка в настройке рефлектора. Неверный формат."):
        Reflector(invalid_reflector_set)


def test_enigma_initial_set_length_mismatch():
    rotor_set = ['АБВГ-ГАБВ', 'АБВГ-БАГВ', 'АБВГ-ВГАБ']
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'
    panel_set = 'БВ'
    # Передаем только две позиции вместо трех
    initial_positions = 'АА'
    with pytest.raises(ValueError, match="Количество начальных позиций не соответствует количеству роторов."):
        Enigma(rotor_set, reflector_set, panel_set, initial_positions)


def test_read_configuration_reflector_line(tmp_path):
    config_file = tmp_path / "test_config.txt"
    config_content = """
    rotor_1 = АБВГ-ГАБВ
    rotor_2 = АБВГ-БАГВ
    reflector = А-Г,Б-В,Г-А,В-Б
    """
    config_file.write_text(config_content, encoding="utf-8")

    rotor_set, reflector_set = read_configuration(config_file)
    assert rotor_set == ['АБВГ-ГАБВ', 'АБВГ-БАГВ'], "Неверно считаны настройки роторов"
    assert reflector_set == 'А-Г,Б-В,Г-А,В-Б', "Неверно считаны настройки рефлектора"

