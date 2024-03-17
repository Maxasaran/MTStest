import os
import datetime

from typing import Dict, Tuple


def prefixes_dict_creator(the_path: str):
    """
    Функция создает из файла с префиксами список вот таких кортежей: (prefix, zone).

    :param the_path: (str) путь до директории с файлом 'PREFIXES.txt'.
    :return: (list[tuple[str, str]]) список кортежей вида: (prefix, zone).

    """
    prefix_path: str = os.path.abspath(the_path)
    prefix_path: str = os.path.join(prefix_path, 'PREFIXES.txt')
    with open(prefix_path, 'r') as f_o_prefix_path:
        return {prefix: zone for zone, prefix in (string_.strip().split(',') for string_ in f_o_prefix_path)}


def prefix_zone_finder(num_as_str: str):
    """
    Рекурсивный алгоритм поиска наиболее соответствующей префиксной зоны.
    Функция должна принимать на вход номер телефона как строку и проверять его наличие в словаре префиксов из глобальной
    области видимости. Если в префикс в словаре не встречается, с конца префикса отбрасывается одна цифра и операция
    повторяется до нахождения префикса или присвоения значения "Unknown".

    :param num_as_str: (str) номер телефона в строчном представлении.
    :return: (tuple[str, str]) кортеж из наиболее релевантного префикса и соответствующей ему зоны.
    """

    if num_as_str in prefixes_dict.keys():
        return num_as_str, prefixes_dict.get(num_as_str)
    elif len(num_as_str) == 1:
        return 'Unknown', ''
    else:
        res = prefix_zone_finder(num_as_str[:-1])

    return res


def synthetic_files_parser(synth_dir_path: str) -> None:
    """
    Функция построчно парсит файлы из директории с синтетическими данными добавляя к исходным файлам окончание "_OLD".
    Из полученных данных сохраняется:
        телефон звонившего - в переменную "msisdn",
        набранный номер - в переменную "dialed",
        длительность звонка для данной пары - в переменную "duration",

    Эти данные прогоняются через функцию prefix_zone_finder и возвращаются в виде кортежей:
        кортеж из префикса и зоны звонившего - в переменную "msisdn_prefix",
        кортеж из префикса и зоны принявшего звонок - в переменную "dialed_prefix",

    Кортеж из зоны звонившего и зоны принявшего звонок сохраняется в переменную "connected_pair",

    Если в ходе обработки строки не возникает исключений, обогащенная новыми данным строка записывается в исходный файл.
    После перебора всех строк бэкап (*.txt_OLD) удаляется.

    :param synth_dir_path: (str) путь до директории с синтетическими данными.
    """
    volumes_txt: dict[tuple[str, str]: list[int, int]] = {}

    for file_ in os.listdir(synth_dir_path):

        try:
            file = os.path.join(synth_dir_path, file_)
            os.rename(file, file + '_OLD')
            with open(file + '_OLD', 'r') as synth_path_fobj_r, open(file, 'a') as synth_path_fobj_a:
                for string_in_synth_file in synth_path_fobj_r:

                    # Получаем строку из файла с синтетическими данными и обрабатываем ее:
                    listed_string: list[str] = string_in_synth_file.split(',')
                    msisdn, dialed = listed_string[5:7]

                    msisdn_prefix, msisdn_zone = prefix_zone_finder(msisdn)
                    dialed_prefix, dialed_zone = prefix_zone_finder(dialed)

                    connected_pair: tuple[str, str] = msisdn_zone, dialed_zone
                    duration: int = int(listed_string[8])

                    # Собираем статистику по каждой паре префиксных зон в словарь volumes_txt:
                    if volumes_txt.get(connected_pair):
                        volumes_txt[connected_pair][0] += 1
                        volumes_txt[connected_pair][1] += duration
                    else:
                        volumes_txt[connected_pair] = [1, duration]

                    # Записываем обогащенные данные обратно в файл с синтетическими данными:
                    listed_string[9:12] = msisdn_prefix, msisdn_zone, dialed_prefix, dialed_zone
                    synth_path_fobj_a.write(",".join(listed_string))

        except Exception as exc:
            # Если возникает исключение, отправляем логи или обрабатываем, как посчитаем нужным.
            print(f'We got some {exc=}, script stopped, report sent to admin =)')
            break
        else:
            # удаляем корректно обработанный (*.txt_OLD) файл с синтетическими данными.
            os.remove(file + '_OLD')

    # Вот здесь сохраняется статистика в файл 'volumes.txt':
    with open('volumes.txt', 'a') as volumes_txt_fobj_a:
        for (zone1, zone2), (count, duration_) in volumes_txt.items():
            volumes_txt_fobj_a.write(f'{zone1},{zone2},{count},{duration_}\n')


if __name__ == "__main__":
    res = datetime.datetime.now()
    print(f'Код пошел выполняться в: {res=}')
    prefixes_dict = prefixes_dict_creator('D:/SCRIPTS/test/test_task/python/KT/var1/Префиксы телефонных номеров (CSV)')
    synthetic_files_parser('D:/SCRIPTS/test/test_task/python/KT/var1/Синтетические данные (CSV)')
    print(f'Время следующее:{datetime.datetime.now() - res}')
