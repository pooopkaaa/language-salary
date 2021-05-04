# Зарплата среди популярных языков программирования

Скрипт для сбора статистики о размере средней зарплаты среди популярных языков программирования с сайтов [superjob.ru](https://www.superjob.ru/) и [hh.ru](https://hh.ru/). Имеется возможность указать город и промежуток времени для поиска нужных данных.

## Установка

- Для работы скрипта у вас должен быть установлен [Python](https://www.python.org/downloads/) (не ниже версии 3.6.0).
- Скачайте код.
- Рекомендуется использовать [virtualenv/env](https://docs.python.org/3/library/venv.html) для изоляции проекта.
- Установите зависимости для работы скрипта.

```sh
pip install -r requirements.txt
```

## Переменные окружения

Создайте файл `.env`, который содержит `SECRETKEY` для доступа к [superjob.ru](https://superjob.ru/). Для получения `SECRETKEY` воспользуйтесь документацией [api.superjob.ru](https://api.superjob.ru/). Запишите в переменную `API_SUPERJOB_SECRETKEY` полученное значение `SECRETKEY`.

```
API_SUPERJOB_SECRETKEY=
```

## Запуск

Для сбора статистики о размере средней зарплаты необходимо запустить скрипт с переданными необязательными параметрами:

Параметр | Пример 1 | Пример 2 | Описание
------- | -------- | -------- | --------
`--town`<br>`-t` | `--town Санкт-Петербург` | `-t Санкт-Петербург` | Укажите город поиска.
`--period`<br>`-p` | `--period 10` | `-p 10` | Укажите промежуток времени в днях от `1` до `30` за который необходимо считать статистику.

Пример запуска с параметрами:

```sh
python main.py -t Санкт-Петербург -p 10
```

При запуске без параметров поиск проходит по городу **Москва** и в промежуток времени **30 дней**:

```sh
python main.py 
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).