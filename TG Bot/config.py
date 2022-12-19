token = "5899204719:AAEqnkTQSdt6o7H-NUqPIrm-qBI2eNgRfeI"
payments_token = "401643678:TEST:85080fc1-f19e-481a-91e1-9736d0b3d925"
import time

import requests
from bs4 import BeautifulSoup
current_year = time.asctime().split()[-1]

# Получение актуального списка команд
response = requests.get(f'https://ru.motorsport.com/f1/standings/{current_year}/?type=Team&class=')
bs = BeautifulSoup(response.text, "lxml")
teamPhotoURLs = bs.find('table', class_='ms-table ms-table--result').find('tbody').find_all('tr', class_='ms-table_row')
teamNames = [team.find_next('span', class_='name').text.split() for team in
             teamPhotoURLs]  # Получаю названия команд с https://ru.motorsport.com/f1/standings/
for team in teamNames:  # убираю лишнее из названий для поиска детальной информации на https://www.f1-world.ru/teams/list.php3
    if team[-1] == 'Racing':
        team.pop(-1)
    elif " ".join(team[-2:]) == 'F1 Team':
        team.pop(-1)
        team.pop(-1)
    teamNames[teamNames.index(team)] = " ".join(team)
teamPhotoURLs = {teamNames[teamPhotoURLs.index(team)]: "https://ru.motorsport.com/" + team.find_next('a',
                                                                                                     class_='ms-link').get(
    'href') for team in teamPhotoURLs}
response = requests.get(f'https://www.f1-world.ru/teams/list.php3')
bs = BeautifulSoup(response.text, "lxml")
teamURLs = bs.find('table', class_='news8').find_all('div', class_='head8')
teamURLs = {team.find_next('a').text: f"https://www.f1-world.ru/{team.find_next('a').get('href')}" for team in
            teamURLs[:-1] if team.find_next(
        'a').text in teamNames}  # берется база со всеми существовавшими командами в Ф1, потом обрезается по списку teamNames, где лежат названия актуальных команд в сезоне

# Получение актуального списка пилотов и их фото
response = requests.get(f'https://ru.motorsport.com/f1/standings/{current_year}/?type=Driver&class=')
bs = BeautifulSoup(response.text, "lxml")
driverPhotoURLs = bs.find('tbody').find_all('tr', class_='ms-table_row')
driverPhotoURLs = {
    " ".join(driver.find_next('span', class_='name').text.split()): "https://ru.motorsport.com" + driver.find_next('a',
                                                                                                                   class_='ms-link').get(
        'href') for driver in driverPhotoURLs}
response = requests.get(f'https://www.f1-world.ru/{current_year}/zachet_pilotov.php')
bs = BeautifulSoup(response.text, "lxml")
driverURLs = bs.find('div', class_='midpart').find('table', class_='f1cup').find_all('a')
driverURLs = {driver.text: "https://www.f1-world.ru/" + driver.get('href') for driver in driverURLs}
driverPhotoURLs['Александр Албон'] = driverPhotoURLs.get('Александр Элбон')
driverPhotoURLs.pop('Александр Элбон')
driverPhotoURLs['Нико Хюлкенберг'] = driverPhotoURLs.get('Нико Хюлькенберг')
driverPhotoURLs.pop('Нико Хюлькенберг')
driverPhotoURLs['Николас Латифи'] = driverPhotoURLs.get('Николя Латифи')
driverPhotoURLs.pop('Николя Латифи')

# Ссылка на сайт с билетами на F1
ticketsToBahrain = "https://www.gpticketshop.com/en/f1/bahrain-f1-grand-prix/tickets.html"
# tickets = {f"{bahrainInfo[0][ticket][0]} | {bahrainInfo[0][ticket][1]} | {bahrainInfo[0][ticket][2]}  {bahrainInfo[1][ticket]}" : f"{bahrainInfo[0][ticket][0]}{bahrainInfo[0][ticket][1]}{bahrainInfo[0][ticket][2]}" for ticket in range(len(bahrainInfo[0]))}
# print(tickets)
# Ссылки на фильмы/сериалы
contentURLs = {"\"Сенна\" 2010 IMDb: 8.50": "https://www.kinopoisk.ru/film/573209/",
               "\"Шумахер\" 2021 IMDb: 7.40": "https://www.kinopoisk.ru/film/4536604/",
               "\"Уильямс\" 2017 IMDb: 7.60": "https://www.kinopoisk.ru/film/1046722/",
               "\"Макларен\" 2017 IMDb: 7.30": "https://www.kinopoisk.ru/film/935410/",
               "\"Гонка\" 2013 IMDb: 8.10": "https://www.kinopoisk.ru/film/596125/",
               "\"Formula 1: Drive to Survive\" 2019 IMDb: 8.60": "https://www.kinopoisk.ru/series/1240162/",
               "\"Гран-при\" 1966 IMDb: 8.10": "https://www.kinopoisk.ru/film/8901/",
               "\"1\" 2013 IMDb: 7.90": "https://www.kinopoisk.ru/film/794704/"
               }

# Словарь с флагами стран для вставки в сообщения
flagsEmoji = {"austria": '🇦🇹',
              "australia": '🇦🇺',
              "azerbaijan": '🇦🇿',
              "bahrain": '🇧🇭',
              "belgium": '🇧🇪',
              "brazil": '🇧🇷',
              "united kingdom": '🇬🇧',
              "uk": '🇬🇧',
              "hungary": '🇭🇺',
              "vietnam": '🇻🇳',
              "germany": '🇩🇪',
              "great britain": '🇬🇧',
              "denmark": '🇩🇰',
              "israel": '🇮🇱',
              "spain": '🇪🇸',
              "italy": '🇮🇹',
              "canada": '🇨🇦',
              "quatar": '🇶🇦',
              "china": '🇨🇳',
              "malaysia": '🇲🇾',
              "mexico": '🇲🇽',
              "monaco": '🇲🇨',
              "netherlands": '🇳🇱',
              "the netherlands": '🇳🇱',
              "united arab emirates": '🇦🇪',
              "uae": '🇦🇪',
              "poland": '🇵🇱',
              "russia": '🇷🇺',
              "singapore": '🇸🇬',
              "switzerland": '🇨🇭',
              "united states": '🇺🇸',
              "usa": '🇺🇸',
              "thailand": '🇹🇭',
              "turkey": '🇹🇷',
              "finland": '🇫🇮',
              "france": '🇫🇷',
              "estonia": '🇪🇪',
              "japan": '🇯🇵',
              "saudi arabia": '🇸🇦',
              "portugal": '🇵🇹'}
# 🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿

# Массив из ID стикеров в телеграме. Используется по команде "Стикеры"
stickerpacks = ["CAACAgQAAxkBAAEGpfVjidIJ-OJcd-DR84v9DxfcDroY7QAC4wwAAhoPsFGDw8akCh-fgSsE",
                "CAACAgQAAxkBAAEGpfdjidI-ubyQz795-N8YmkV7IDSw-QACBMADAAFD38I1e7lVMhREHDIrBA",
                "CAACAgIAAxkBAAEGpgJjidPAka2s6d8Wxb_KeuPxb6Kg5QACKAQAAnM9WwuOz_wCAi_CtisE",
                "CAACAgIAAxkBAAEGpghjidQLqHhJGcs47Zie2FkantTWoQACMRQAAvZg0Unn9TfgqHmtMSsE",
                "CAACAgIAAxkBAAEGqeFji1BezdE42FHjdQNr18MGqL6OuAACmAIAAlChKwABFcX1V3DG8qcrBA",
                "CAACAgIAAxkBAAEGqeNji1B3qhgcC2WuL-JqcTWe8OKLuAACVRwAAn5byErEJYGTefiyjisE",
                "CAACAgIAAxkBAAEGqCpjipTRnzS8XjwM3Y0RUY3hYyVBfwACohAAAjIeYUmaiUKNu0M0rSsE",
                "CAACAgIAAxkBAAEGqCxjipTcMtauWfE3Hkjq2lnAU0PgAgACFQAD2zEKHZHMCFhP1YM-KwQ",
                "CAACAgIAAxkBAAEGqC5jipTjuCLqnSKLeaBHT374ieEVzQACmRAAAkSqcUhZtbrWSkubxSsE"]

# Ссылки на ресурсы, на которых можно смотреть трансляции
liveURLs = {"Simply Formula": "https://vk.com/simply_formula",
            "Be on Edge": "https://vk.com/be_on_edge",
            "Topracing": "https://vk.com/top_racing"
            }
