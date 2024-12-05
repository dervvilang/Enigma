import pytest
from enigma import Enigma, Rotor, Reflector, Panel


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
        # некорректная панель изза отсутствия одного символа
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
    rotor_set2 = ['АБВГ-ВБАГ', 'АБВГ-БАГВ', 'АБВГ-ГАБВ']  # Один ротор заменён
    reflector_set = 'А-Г,Б-В,В-Б,Г-А'
    panel_set = 'БВ'

    # оригинальная машина для шифрования
    enigma1 = Enigma(rotor_set1, reflector_set, panel_set, 'ААА')
    input_text = 'АБВ'
    encrypted_text = enigma1.encryption_text(input_text)

    # машина с другим набором роторов для дешифровки
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