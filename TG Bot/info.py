import os
import time

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from config import flagsEmoji, ticketsToBahrain, current_year, teamURLs, teamPhotoURLs, driverURLs, driverPhotoURLs
import random

def openDB():
    from database import BotDB
    BotDB = BotDB('F1Assistant.db')
    return BotDB


translator = Translator()


def getCalendar(year, *toUpdate):
    database = openDB()
    if ((not database.year_exists(year)) or (toUpdate == True)) and (year <= current_year):
        responce = requests.get(f'https://ru.motorsport.com/f1/schedule/{year}')
        bs = BeautifulSoup(responce.text, 'lxml')
        try:
            GP_Links = bs.find_all('tr', class_='ms-schedule-table__item-main')
            for i in GP_Links:
                if i.find_next('div', class_='ms-schedule-table-item-main__info').find_next('a', class_='ms-link').get(
                        'href')[:4] == "/f1/":
                    GP_Link = "https://ru.motorsport.com" + i.find_next('div',
                                                                        class_='ms-schedule-table-item-main__info').find_next(
                        'a', class_='ms-link').get('href')
                    GP_Links[GP_Links.index(i)] = GP_Link
                else:
                    GP_Data = i.find_next('div', class_='ms-schedule-table-date ms-schedule-table-date--your').find_all(
                        'span')
                    GP_Data = [data.text for data in GP_Data]
                    GP_Data[0] = f"{''.join(list(GP_Data[0])[:-2])} {GP_Data[1]}"
                    GP_Data.remove(GP_Data[1])
                    GP_Data.append(i.find_next('h2').text)
                    GP_Data.append(
                        f"{translator.translate(translator.translate(i.find_next('h2').text.split()[-1], dest='en').text, dest='ru').text} {flagsEmoji.get(translator.translate((i.find_next('h2').text.split())[-1], dest='en').text.lower())}")
                    GP_Data.append(i.find_next('td',
                                               class_='ms-schedule-table__cell ms-schedule-table__cell--status ms-schedule-table__cell--status-finished').text)
                    GP_Links[GP_Links.index(i)] = GP_Data
        except AttributeError:
            calendar = f"<b>Я не нашел календарь Формулы-1 сезона {year} 😞</b>\nПопросите его у меня позже, возможно я смогу его вам показать"
            return calendar
        GPs = []
        calendar = f"<b>Календарь сезона Формулы-1 {year}:</b>\n"
        for link in GP_Links:
            if link[:5] == "https":
                responce = requests.get(link)
                bs = BeautifulSoup(responce.text, 'lxml')
                try:
                    GP_Info = [
                        " ".join(bs.find('div', class_='ms-entity-header_wrapper ms-ml').find('h1').text.split()[:-1]),
                        [i.text for i in bs.find_all('span', class_='ms-event-header-period_day')],
                        [i.text for i in bs.find_all('span', class_='ms-event-header-period_month')],
                        [bs.find('div', class_='ms-event-header_location').find('span').text,
                         bs.find('div', class_='ms-event-header_location').find('a').text],
                        bs.find('span', class_='ms-schedule-item_results-title').text,
                    ]
                    GP_Info = [GP_Info[0], GP_Info[1][0] + " " + GP_Info[2][0], GP_Info[1][1] + " " + GP_Info[2][1],
                               GP_Info[3][0],
                               translator.translate(str(GP_Info[3][0]), dest='en').text.lower(), GP_Info[3][1],
                               GP_Info[
                                   4]]  # переопределяю переменную, чтобы все данные были в удобном одномерном списке [Имя мероприятия, дата начала, дата конца, страна, код для флага страны, Трасса, Статус мероприятия]
                    GPs.append(GP_Info)
                except AttributeError:
                    if (GP_Links.index(link) + 1) != len(GP_Links):
                        continue
                    else:
                        if len(GPs) != 0:
                            for GP in GPs:
                                calendar += f"\n{GPs.index(GP) + 1}.  <b>{GP[0]}</b>    {GP[1]} — {GP[2]}" \
                                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Страна:</b> {GP[3]} {flagsEmoji.get(GP[4])}" \
                                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Трасса:</b> {GP[5]}" \
                                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Статус:</b> {GP[6]}\n"
                            return calendar
                        else:
                            calendar = f"<b>Я не нашел календарь Формулы-1 сезона {year} 😞</b>\nПопросите его у меня позже, возможно я смогу его вам показать"
                            return calendar
            else:
                GPs.append(link)
        for GP in GPs:
            if len(GP) != 4:
                calendar += f"\n{GPs.index(GP) + 1}.  <b>{GP[0]}</b>    {GP[1]} — {GP[2]}" \
                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Страна:</b> {GP[3]} {flagsEmoji.get(GP[4])}" \
                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Трасса:</b> {GP[5]}" \
                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Статус:</b> {GP[6]}\n"
            else:
                calendar += f"\n{GPs.index(GP) + 1}.  <b>{GP[1]}</b>    {GP[0]}" \
                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Страна:</b> {GP[2]}" \
                            f"\n    {len(str(GPs.index(GP) + 1)) ** 2 * ' '}<b>Статус:</b> {GP[3]}\n"
        database.add_info_calendar(year, calendar)
    else:
        if year > current_year:
            calendar = f"<b>Я не нашел календарь Формулы-1 сезона {year} 😞</b>\nПопросите его у меня позже, возможно я смогу его вам показать"
            return calendar
        calendar = database.get_calendar(str(year))[0][0]
    database.close()
    return calendar


def getTeamInfo(url, urlPhoto, *toUpdate):
    database = openDB()
    countOfExtraMessages = 1
    response = requests.get(url)
    bs = BeautifulSoup(response.text, "lxml")
    teamName = " ".join(bs.find('h1').text.split())
    if (not database.team_exists(teamName)) or (toUpdate == True):
        teamData = bs.find('table').find('div', class_='midpart').find_all('tr')[3]
        # Ниже teamShortedData хранит значения со всей страницы (на примере команды Вильямс) (Великобритания, Аргентина'1975...)
        teamData = teamData.find_all_next('tr')[0].find_all_next('div', class_='news8')
        teamData = [data.text.split() for data in teamData][:-3]
        debut = ", ".join(teamData[1][0].split("\'"))
        teamShortedInfo = f"<b>{teamName}</b>" \
                          f"\n\n<b>Cтрана:</b> {teamData[0][0]} {flagsEmoji.get(translator.translate(teamData[0][0], dest='en').text.lower())}" \
                          f"\n<b>Дебют:</b> {debut}"
        teamDetailedInfo_1 = f"<b>Статистика команды:</b>\n\n"
        if " ".join(bs.find('table', class_='f1menu').find_all('div', class_='news8b')[
                        9].text.split()) != 'Кубки конструкторов':
            teamDetailedInfo_1 += f"<b>Лучшее место в Кубке конструкторов:</b> {teamData[12][0]}"
        else:
            teamDetailedInfo_1 += f"<b>Кубки конструкторов:</b> {teamData[12][0]} 🏆"
        if " ".join(
                bs.find('table', class_='f1menu').find_all('div', class_='news8b')[
                    8].text.split()) != 'Чемпионские титулы':
            teamDetailedInfo_1 += f"\n<b>Лучшее место в чемпионате пилотов:</b> {teamData[11][0]}"
        else:
            teamDetailedInfo_1 += f"\n<b>Чемпионские титулы пилотов:</b> {teamData[11][0]} 🏆"
        teamDetailedInfo_1 += f"\n<b>Участий в Гран-при:</b> {teamData[3][0]}" \
                              f"\n<b>Cтарты в Гран-при:</b> {teamData[5][0]}"
        if "".join(bs.find('table', class_='f1menu').find_all('div', class_='news8b')[4].text.split()) != 'Победы':
            teamDetailedInfo_1 += f"\n<b>Лучшее место в гонке:</b> {teamData[7][0]}"
        else:
            teamDetailedInfo_1 += f"\n<b>Подиумы:</b> {teamData[6][0]}" \
                                  f"\n— Победы: {teamData[7][0]} 🥇"
        teamDetailedInfo_1 += f"\n<b>Поул-позиции:</b> {teamData[4][0]}" \
                              f"\n<b>Первые линии:</b> {teamData[6][0]}" \
                              f"\n<b>Лучшие круги:</b> {teamData[8][0]}" \
                              f"\n<b>Зачетные очки:</b> {teamData[10][0]}\n\n"
        yearStatistics = []
        teamDetailedInfo_2 = f"<b>Год Команда — Производитель двигателей</b> — Старты — Очки — Подиумы — Победы — Поул-позиции — Лучшие круги — Место в кубке конструкторов\n\n"
        teamDetailedInfo_3 = ""
        for dataUnit in teamData[13:]:
            if len(yearStatistics) < 3:
                if len(dataUnit) == 1 and dataUnit != [] and len(dataUnit[0]) == 4:
                    yearStatistics.append(dataUnit[0])
                    continue
                if len(dataUnit) not in [1, 2] and len(yearStatistics) != 2:
                    motorCompanyName = ""
                    for data in dataUnit:
                        if data not in teamName.split() and list(data)[0] != '(':
                            motorCompanyName += f"{data} "
                        elif list(data)[0] == '(' and len(yearStatistics) == 1:
                            if motorCompanyName == "":
                                yearStatistics.append(teamName)
                            else:
                                yearStatistics.append(motorCompanyName)
                            break
                if len(yearStatistics) == 2:
                    fullTeamName = dataUnit[dataUnit.index(yearStatistics[-1].split()[-1]) + 1: dataUnit.index('-')]
                    if len(fullTeamName) == 1:
                        fullTeamName = "".join(list(fullTeamName[0])[1:-1])
                    else:
                        fullTeamName = f"{''.join(list(fullTeamName[0])[1:])} {' '.join(fullTeamName[1:-1])} {''.join(list(fullTeamName[-1][:-1]))}"
                    yearStatistics.append(fullTeamName)
                continue
            else:
                if dataUnit == []:
                    dataUnit = '0'
                    yearStatistics.append(dataUnit)
                    continue
                elif (len(dataUnit) == 2 and dataUnit[1] == 'место') or (dataUnit == ['=']):
                    if dataUnit == ['=']:
                        dataUnit = ["н/м"]
                    yearStatistics.append(" ".join(dataUnit))
                    if len(teamDetailedInfo_2) + len(
                            f"<b>{yearStatistics[0]} {yearStatistics[2]} — {yearStatistics[1]}</b>" \
                            f" — {' — '.join(yearStatistics[3:])}\n") <= 4096:
                        teamDetailedInfo_2 += f"<b>{yearStatistics[0]} {yearStatistics[2]} — {yearStatistics[1]}</b>" \
                                              f" — {' — '.join(yearStatistics[3:])}\n"
                    else:
                        teamDetailedInfo_3 += f"<b>{yearStatistics[0]} {yearStatistics[2]} — {yearStatistics[1]}</b>" \
                                              f" — {' — '.join(yearStatistics[3:])}\n"
                    yearStatistics = []
                    continue
                else:
                    yearStatistics.append(dataUnit[0])
        if teamDetailedInfo_3 != "":
            countOfExtraMessages += 1
            teamDetailedInfo_3 += f"\n<b>н/м</b> — Нет места"
        response = requests.get(urlPhoto)
        bs = BeautifulSoup(response.text, "lxml")
        teamDrivers = [driver.get('alt') for driver in bs.find('div', class_='ms-grid ms-grid-vert').find_all('img')]
        teamShortedInfo += f"\n<b>Текущий состав пилотов:</b> {teamDrivers[0]}, {teamDrivers[1]}"
        teamLogo = bs.find('div', class_='ms-entity-header_img-wrapper').find('img',
                                                                              class_='ms-item_img ms-item_img--3_2').get(

            'src')
        if not os.path.exists('teamPics/'):
            os.mkdir('teamPics/')
        imageData = requests.get(teamLogo, verify=False).content
        with open('teamPics/' + teamName + '.jpg', 'wb') as handler:
            handler.write(imageData)
        teamDetailedInfo = [teamDetailedInfo_1, teamDetailedInfo_2, teamDetailedInfo_3]
        database.add_info_team(teamName, teamDetailedInfo_1, teamDetailedInfo_2, teamDetailedInfo_3, teamShortedInfo,
                               teamDrivers[0], teamDrivers[1], countOfExtraMessages)
        return teamDetailedInfo, teamName, teamShortedInfo, teamDrivers, countOfExtraMessages
    else:
        if not os.path.exists('teamPics/'):
            os.mkdir('teamPics/')
            response = requests.get(urlPhoto)
            bs = BeautifulSoup(response.text, "lxml")
            teamLogo = bs.find('div', class_='ms-entity-header_img-wrapper').find('img',
                                                                                  class_='ms-item_img ms-item_img--3_2').get(

                'src')
            imageData = requests.get(teamLogo, verify=False).content
            with open('teamPics/' + teamName + '.jpg', 'wb') as handler:
                handler.write(imageData)
        elif not os.path.exists('teamPics/' + teamName + '.jpg'):
            response = requests.get(urlPhoto)
            bs = BeautifulSoup(response.text, "lxml")
            teamLogo = bs.find('div', class_='ms-entity-header_img-wrapper').find('img',
                                                                                  class_='ms-item_img ms-item_img--3_2').get(

                'src')
            imageData = requests.get(teamLogo, verify=False).content
            with open('teamPics/' + teamName + '.jpg', 'wb') as handler:
                handler.write(imageData)
        team_return = database.get_info_team(teamName)
        database.close()
        return team_return[0], team_return[1], team_return[2], team_return[3], team_return[4]


def getDriverInfo(url, urlPhoto, *toUpdate):
    database = openDB()
    response = requests.get(url)
    bs = BeautifulSoup(response.text, "lxml")
    driverName = " ".join(bs.find('h1').text.split())
    if ((not database.driver_exists(driverName)) or (toUpdate == True)):
        driverShortedInfo = bs.find('table').find('div', class_='midpart').find('table').find('table').find('tr')
        driverShortedInfo = driverShortedInfo.find_all('div', class_='news8')
        driverShortedInfo = [dataUnit.text.split() for dataUnit in driverShortedInfo][:-1]
        driverShortedInfo = ["".join(list(driverShortedInfo[1][-1])[1:-1]), ", ".join(
            driverShortedInfo[2][0].split('\''))]  # страна рождения, дебют
        driverShortedInfo[0] = driverShortedInfo[0].split("(")[-1]
        driverShortedInfo[
            0] = f"{driverShortedInfo[0]} {flagsEmoji.get(translator.translate(driverShortedInfo[0], dest='en').text.lower())}"
        driverUnprocessedStatistics = bs.find('table').find('div', class_='midpart').find('table').find(
            'table').find_all(
            'table')
        if driverUnprocessedStatistics[0].find('div', class_='news8b', text='\nЛучшее место в гонке'):
            winOrHighestPosition = "Лучшее место в гонке"
        else:
            winOrHighestPosition = "Победы:"
        driverUnprocessedStatistics = [table.find_all('div', class_='news8') for table in driverUnprocessedStatistics]
        driverUnprocessedStatistics = [["".join(one_div.text.split()) for one_div in driverUnprocessedStatistics[0]],
                                       [" ".join(one_div.text.split()) for one_div in driverUnprocessedStatistics[1]]]
        driverWorldChampionshipWins = driverUnprocessedStatistics[1].count('1 место')
        driverStatistics = f"<b>Статистика пилота:</b>" \
                           f"\n\n<b>Чемпионские титулы: </b>{driverWorldChampionshipWins} 🏆" \
                           f"\n<b>Участия в Гран-При:</b> {driverUnprocessedStatistics[0][0]}" \
                           f"\n<b>Старты в Гран-При:</b> {driverUnprocessedStatistics[0][2]}"
        if winOrHighestPosition != "Победы:":
            driverStatistics += f"\n<b>Лучшее место в гонке:</b> {driverUnprocessedStatistics[0][4]}"
            driverUnprocessedStatistics[0][4] = 0
        driverStatistics += f"\n<b>Подиумы:</b> {driverUnprocessedStatistics[0][1]}" \
                            f"\n— Победы: {driverUnprocessedStatistics[0][4]} 🥇" \
                            f"\n— 2 места: {driverUnprocessedStatistics[0][6]}  🥈" \
                            f"\n— 3 места: {driverUnprocessedStatistics[0][8]}  🥉" \
                            f"\n<b>Поул-позиции:</b> {driverUnprocessedStatistics[0][3]}" \
                            f"\n<b>Первые линии:</b> {driverUnprocessedStatistics[0][5]}" \
                            f"\n<b>Лучшие круги:</b> {driverUnprocessedStatistics[0][7]}" \
                            f"\n<b>Зачетные очки:</b> {driverUnprocessedStatistics[0][9]}\n\n"
        detailedStatistics = []
        yearList = []
        for data in driverUnprocessedStatistics[1]:
            if data == '':
                data = '0'
            if "".join(list(data[-5:])) in ['место', '=']:
                if data == '=' and yearList[2] == '0':
                    yearList = []
                    continue
                else:
                    yearList.append(data)
                detailedStatistics.append(yearList)
                yearList = []
                continue
            if ("".join(list(data)[:2]) == '20' and len(list(data)) == 4) and len(yearList) == 8:
                yearList.append(detailedStatistics[-1][-1])
                detailedStatistics.append(yearList)
                yearList = []
            if yearList == [] and ("".join(list(data)[:2]) != '20' and len(list(data)) != 4):
                yearList = [detailedStatistics[-1][0]]
            yearList.append(data)
        driverStatistics += f"<b>Год Команда</b> — Старты — Очки — Подиумы — Победы — Поул-позиции — Лучшие круги — Место в личном зачете\n\n"
        for year in detailedStatistics:
            driverStatistics += f"<b>{' '.join(year[:2])}</b> — {' — '.join(year[2:-1])} — {year[-1].split()[0]}\n"
        response = requests.get(urlPhoto)
        bs = BeautifulSoup(response.text, "lxml")
        driverNationality = bs.find('img', class_='ms-entity-header_flag').get('title').lower()
        driverNationality = f"{translator.translate(driverNationality, dest='ru').text.capitalize()} {flagsEmoji.get(driverNationality)}"
        driverAgeData = bs.find('div', class_='ms-entity-header_start').find('span',
                                                                             class_='ms-entity-header_age').text.split()
        driverAgeData = [int("".join(driverAgeData[-1].split(')'))), list(map(int, driverAgeData[0].split('-')))]
        try:
            teamName = bs.find('div', class_='ms-entity-header_start').find('a',
                                                                            class_='ms-driver-header_team-title ms-link').text
            driverNumber = bs.find('div', class_='ms-driver_number ms-mr').text
        except AttributeError:
            teamName = "Нет команды"
            driverNumber = "(Нет номера)"

        driverInfo = (f"<b>{driverName} №{driverNumber}</b>\n\n"
                      f"<b>Команда:</b> {teamName}\n"
                      f"<b>Возраст:</b> {driverAgeData[0]}\n"
                      f"<b>Дата рождения:</b> {driverAgeData[1][2]}.{driverAgeData[1][1]}.{driverAgeData[1][0]}\n"
                      f"<b>Место рождения:</b> {driverShortedInfo[0]}\n"
                      f"<b>Гражданство:</b> {driverNationality}\n"
                      f"<b>Дебют в Формуле-1:</b> {driverShortedInfo[1]}\n\n")
        response = requests.get(urlPhoto)
        bs = BeautifulSoup(response.text, "lxml")
        if not os.path.exists('driverPics/'):
            os.mkdir('driverPics/')
        driverPhoto = bs.find('img', class_="ms-item_img ms-item_img--3_2").get('src')
        imageData = requests.get(driverPhoto, verify=False).content
        if not os.path.exists('driverPics/' + driverName + '.jpg'):
            with open('driverPics/' + driverName + '.jpg', 'wb') as handler:
                handler.write(imageData)
        database.add_info_driver(driverStatistics, driverName, driverInfo)
    else:
        if not os.path.exists('driverPics/'):
            os.mkdir('driverPics/')
            response = requests.get(urlPhoto)
            bs = BeautifulSoup(response.text, "lxml")
            teamLogo = bs.find('div', class_='ms-entity-header_img-wrapper').find('img',
                                                                                  class_='ms-item_img ms-item_img--3_2').get(

                'src')
            imageData = requests.get(teamLogo, verify=False).content
            with open('driverPics/' + driverName + '.jpg', 'wb') as handler:
                handler.write(imageData)
        elif not os.path.exists('driverPics/' + driverName + '.jpg'):
            response = requests.get(urlPhoto)
            bs = BeautifulSoup(response.text, "lxml")
            teamLogo = bs.find('div', class_='ms-entity-header_img-wrapper').find('img',
                                                                                  class_='ms-item_img ms-item_img--3_2').get(

                'src')
            imageData = requests.get(teamLogo, verify=False).content
            with open('driverPics/' + driverName + '.jpg', 'wb') as handler:
                handler.write(imageData)
        driver_info = database.get_info_driver(driverName)
        return driver_info
    database.close()
    return driverStatistics, driverName, driverInfo

def tickets_to_BahrainGP(*toUpdate):
    database = openDB()
    GPPhotoName = "BahrainGP.jpg"
    BahrainGPTicketTypes = []
    BahrainGPTicketPrices = []
    if toUpdate:
        response = requests.get(ticketsToBahrain)
        bs = BeautifulSoup(response.text, 'lxml')
        BahrainGPTicketTypes = bs.find('div', class_='table table_grandstandtickets').find_next('div', class_='tablebody').find_all('div', class_='product cell')
        BahrainGPTicketTypes = [[" ".join(ticketType.find_next('strong').text.split()[:-1]), "".join(ticketType.find_next('strong').text.split()[-1].split(ticketType.find_next('span', class_='producttime').text)), ticketType.find_next('span', class_='producttime').text] for ticketType in BahrainGPTicketTypes]
        BahrainGPTicketPrices = bs.find('div', class_='table table_grandstandtickets').find_next('div', class_='tablebody').find_all('div', class_='price cell')
        BahrainGPTicketPrices = [" ".join(ticketPrice.text.split()) for ticketPrice in BahrainGPTicketPrices]
        database.add_ticket_info(BahrainGPTicketTypes, BahrainGPTicketPrices)
    else:
        tickets = database.get_tickets()
        for i in range(len(tickets)):
            if BahrainGPTicketTypes.count(list(tickets[i][:-1])) == 0:
                BahrainGPTicketTypes.append(list(tickets[i][:-1]))
                BahrainGPTicketPrices.append(tickets[i][-1])
    database.close()
    return BahrainGPTicketTypes, BahrainGPTicketPrices, GPPhotoName
tickets_to_BahrainGP(True)

def update_info():
    database = openDB()
    last_update = database.get_last_update_time()
    if (time.time() - last_update > 604800):
        getCalendar(current_year, True)
        for team in teamURLs.keys():
            getTeamInfo(teamURLs.get(team), teamPhotoURLs.get(team), True)
        for driver in driverURLs.keys():
            getDriverInfo(driverURLs.get(driver), driverPhotoURLs.get(driver), True)
        database.log_update_time(time.time())
    elif (time.time() - last_update > 3600):
        tickets_to_BahrainGP(True)
    database.close()

update_info()
