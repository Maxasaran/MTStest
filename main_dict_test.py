import os
import pytest
import allure
from main_dict import synthetic_files_parser, prefixes_dict_creator, prefix_zone_finder

#Путь к тестовым данным
PREFIXES_DATA = r'/home/user/PycharmProjects/MTStestproject/prefixes'
SYNTHETIC_DATA_DIR = r'/home/user/PycharmProjects/MTStestproject/synthetisCDRdata'

#Результат исполнения prefixes_dict_creator для дальнейшей проверки
@pytest.fixture
def prefixes_dict():
    return prefixes_dict_creator(PREFIXES_DATA)

#Результат набор телефонных номеров из тестовых CDR данных
@pytest.fixture
def phone_numbers_set():
    phone_numbers = []
    for filename in os.listdir(SYNTHETIC_DATA_DIR):
        if filename.endswith('.TXT'):
            with open(os.path.join(SYNTHETIC_DATA_DIR, filename), 'r') as file:
                for line in file:
                    parts = line.split(',')
                    phone_numbers.extend([parts[5], parts[6]])
    return set(phone_numbers)

    
##############    

@allure.feature('Тест функции создания списка кортежей (prefix, zone)')

@allure.story('Проверка на тип (Dict)')
def test_prefixes_dict_creator_on_type(prefixes_dict):
    assert isinstance(prefixes_dict, dict), "Output should be a dictionary"
    
@allure.story('Проверка на соответствие типу key:value (Str)')
def test_prefixes_dict_creator_on_element_type(prefixes_dict):
    for prefix, zone in prefixes_dict.items():
        assert isinstance(prefix, str), f"Prefix '{prefix}' is not a string"
        assert isinstance(zone, str), f"Zone '{zone}' for prefix '{prefix}' is not a string"

@allure.story('Проверка префикса на состав элементов: 123456789 или пустая строка (Str)')
def test_prefixes_dict_creator_on_prefix_consist(prefixes_dict):
    for prefix, zone in prefixes_dict.items():
        assert prefix.isdigit() or prefix == '', f"Prefix '{prefix}' is not numeric or empty"
        
##############
        
@allure.feature('Тест функции prefix_zone_finder')

@allure.story('Проверка корректности работы алгоритма функции')
def test_prefix_zone_finder_in_correct_prefix_match(phone_numbers_set, prefixes_dict):
    for phone_number in phone_numbers_set:
        #Прогоняем через функцию prefix_zone_finder тестовое множество номеров phone_numbers_set
        #Присваивая, соответсвующий префикс
        prefix, zone = prefix_zone_finder(phone_number)
        #Проверяем, что найденный префикс является самым длинным совпадением из prefixes_dict
        longest_prefix = max((p for p in prefixes_dict if phone_number.startswith(p)), key=len, default='')
        expected_zone = prefixes_dict.get(longest_prefix, '')

        assert prefix == longest_prefix, f"Expected prefix for '{phone_number}' to be '{longest_prefix}', got '{prefix}'"
        assert zone == expected_zone, f"Expected zone for '{phone_number}' to be '{expected_zone}', got '{zone}'"
       
@allure.story('Проверка наличия соответсвующего префикса в словаре')
def test_prefix_zone_finder_prefix_presence_in_dict(phone_numbers_set, prefixes_dict):
    for phone_number in phone_numbers_set:
        prefix, _ = prefix_zone_finder(phone_number)
        assert prefix in prefixes_dict, f"Prefix '{prefix}' not found in prefixes_dict"    
    
@allure.story('Соответствие префикс - зона')
def test_prefix_zone_finder_correct_zone_matching_in_dict(phone_numbers_set, prefixes_dict):
    for phone_number in phone_numbers_set:
        prefix, zone = prefix_zone_finder(phone_number)
        assert prefixes_dict.get(prefix, '') == zone, f"Zone '{zone}' for prefix '{prefix}' does not match expected zone in prefixes_dict"
        
@allure.story('Проверка на Unknown зону в случае если для номера не нашлось подходящей зоны')
def test_prefix_zone_finder_unmatched_phone_numbers(phone_numbers_set, prefixes_dict):
    for phone_number in phone_numbers_set:
        _, zone = prefix_zone_finder(phone_number)
        if not any(phone_number.startswith(p) for p in prefixes_dict):
            assert zone == 'Unknown', "Expected 'Unknown' zone for unmatched phone number"

##############
        
def file_content(filepath):
    with open(filepath, 'r') as file:
        return file.readlines()

@allure.feature('Тест функции synthetic_files_parser')

@allure.story('Обогащение CDR файлов')
def test_synthetic_files_parser_on_enrich_cdr_files(prefixes_dict):
    #Данные до изменения
    original_contents = {f: file_content(os.path.join(SYNTHETIC_DATA_DIR, f)) 
                         for f in os.listdir(SYNTHETIC_DATA_DIR) if f.endswith('.TXT')}
    #Прогоняем функцию synthetic_files_parser по данным
    synthetic_files_parser(SYNTHETIC_DATA_DIR)
    #Данные после изменения
    enriched_contents = {f: file_content(os.path.join(SYNTHETIC_DATA_DIR, f)) 
                         for f in os.listdir(SYNTHETIC_DATA_DIR) if f.endswith('.TXT')}
    #Сравниваем что данные были изменены
    for filename in original_contents:
        assert original_contents[filename] != enriched_contents[filename], f"{filename} not enriched properly"

@allure.story('Проверка на идемпонентность')
def test_synthetic_files_parser_on_idempotency(prefixes_dict):
    #Измененные данные
    enriched_contents = {f: file_content(os.path.join(SYNTHETIC_DATA_DIR, f))
                         for f in os.listdir(SYNTHETIC_DATA_DIR) if f.endswith('.TXT')}
    #Повторный запуск функции synthetic_files_parser                 
    synthetic_files_parser(SYNTHETIC_DATA_DIR)
    
    #Данные измененные "повторно"
    second_enrichment_contents = {f: file_content(os.path.join(SYNTHETIC_DATA_DIR, f))
                                  for f in os.listdir(SYNTHETIC_DATA_DIR) if f.endswith('.TXT')}
    #Сравнение
    for filename, content in enriched_contents.items():
        assert content == second_enrichment_contents[filename], f"File {filename} content changed after second run."

@allure.story('Проверка на удаление временных файлов')
def test_synthetic_files_parser_on_temporary_files_cleanup():
    #Проверка на наличие файлов с расширением .txt_OLD
    for filename in os.listdir(SYNTHETIC_DATA_DIR):
        assert not filename.endswith('_OLD'), "Temporary file was not cleaned up."
   

###############
    