import logging

# Создание объекта логгера
logger = logging.getLogger()

# Создание объекта обработчика файлового логирования
handler = logging.FileHandler('example.log')

# Настройка уровня логирования
handler.setLevel(logging.CRITICAL)

# Настройка формата сообщений
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(handler)

# Примеры использования логирования
# logger.debug('Это отладочное сообщение')
# logger.info('Это информационное сообщение')
# logger.warning('Это предупреждение')
# logger.error('Это сообщение об ошибке')
# logger.critical('Это критическая ошибка')
