#README#
# Необходимые библиотеки расположены в файле requirements.txt
# Для запуска тестов и создания Allure report в консоли IDE, где запущен проект необходимо выполнить команду:

#    pytest --alluredir=/path/to/allure/results # /path/to/allure/results собственно путь куда планируется сохранить репорт
	
#Для создания HTML report на основе полученных результатов необходимо выполнить команду:
#Результаты расположены здесь:/path/to/allure/results, репорт сохраняется сюда /path/to/allure/report

#    allure generate /path/to/allure/results -o /path/to/allure/report --clean
	
#Для открытия HTML report необходимо выполнить команду:

#	open /path/to/allure/report/index.html
	
#Скорее всего политики безопасности браузера запретит открывать данную страницу.
#Поэтому воспользуемся встроенным http-сервером Python:

#   cd path/to/your/allure-report #переходим в директорию , где расположен html репорт
#	python -m http.server # запускаем http server. В консоли отобразится: Serving HTTP on :: port 8000 (http://[::]:8000/) ...

#Запускаем браузер и переходим на http://localhost:8000, проверяем результат тестов сформированных в Allure Report
