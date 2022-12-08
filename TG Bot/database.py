import sqlite3


class BotDB:

    def __init__(self, db_file):
        """Инициализация соединения с БД"""
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    def year_exists(self, year):
        """Проверяем, есть ли год в БД"""
        result = self.cursor.execute("SELECT year FROM 'calendars' WHERE year = ?", (year,))
        return bool(len(result.fetchall()))

    def team_exists(self, team):
        """Проверяем, есть ли команда в БД"""
        result = self.cursor.execute("SELECT team FROM 'teams' WHERE team = ?", (team,))
        return bool(len(result.fetchall()))

    def driver_exists(self, driver):
        """Проверяем, есть ли пилот в БД"""
        result = self.cursor.execute("SELECT driver FROM 'drivers' WHERE driver = ?", (driver,))
        return bool(len(result.fetchall()))

    def add_year(self, year):
        """Добавляем год в БД"""
        self.cursor.execute("INSERT INTO 'calendars_years' ('year') VALUES (?)", (year,))
        return self.connect.commit()

    def get_calendar(self, year):
        """Получаем календарь по году"""
        calendar = self.cursor.execute("""SELECT calendar FROM 'calendars' WHERE year = ?""", (year,))
        calendar = calendar.fetchall()
        return calendar

    def add_info_calendar(self, year, calendar):
        """Создаем запись для календаря"""
        self.cursor.execute("INSERT INTO 'calendars' ('year', 'calendar') VALUES (?, ?)",
                            (year,
                             calendar))
        return self.connect.commit()

    def add_info_team(self, teamName, detailed_info_1, detailed_info_2, detailed_info_3, shorted_info, team_driver_1,
                      team_driver_2, count_of_extra_messages):
        """Создаем запись для команды"""
        self.cursor.execute(
            "INSERT INTO 'teams' ('team', 'detailed_info_1', 'detailed_info_2', 'detailed_info_3', 'shorted_info', 'team_driver_1', 'team_driver_2', 'count_of_extra_messages') VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (teamName,
             detailed_info_1,
             detailed_info_2,
             detailed_info_3,
             shorted_info,
             team_driver_1,
             team_driver_2,
             count_of_extra_messages
             ))
        return self.connect.commit()

    def add_info_driver(self, driverStatistics, driverName, driverInfo):
        """Создаем запись для пилота"""
        self.cursor.execute(
            "INSERT INTO 'drivers' ('driver', 'driver_statistics', 'driver_info') VALUES (?, ?, ?)",
            (driverName,
             driverStatistics,
             driverInfo
             ))
        return self.connect.commit()

    def get_info_driver(self, driverName):
        """Получаем информацию по команде"""
        driver_info = self.cursor.execute("""SELECT * FROM 'drivers' WHERE driver = ?""", (driverName,))
        driver_info = driver_info.fetchall()
        return driver_info[0][1], driver_info[0][0], driver_info[0][2]

    def get_info_team(self, teamName):
        """Получаем календарь по году"""
        team_info = self.cursor.execute("""SELECT * FROM 'teams' WHERE team = ?""", (teamName,))
        team_info = team_info.fetchall()[0]
        team_detailed_info = [team_info[1], team_info[5], team_info[6]]
        team_drivers = [team_info[3], team_info[7]]
        return team_detailed_info, team_info[0], team_info[2], team_drivers, team_info[4]

    def log_update_time(self, time):
        """Записываем время последнего обновления"""
        if len(self.cursor.execute("""SELECT rowid FROM 'update_logs' WHERE rowid = ?""", (1,)).fetchall()) == 0:
            self.cursor.execute("""INSERT INTO 'update_logs' ('update_time') VALUES (?)""",
                                (time,))
        else:
            self.cursor.execute("""UPDATE update_logs SET update_time = ? WHERE rowid = 1""",
                                (time,))
        return self.connect.commit()

    def get_last_update_time(self):
        """Получаем время последнего обновления"""
        if len(self.cursor.execute("""SELECT rowid FROM 'update_logs' WHERE rowid = ?""", (1,)).fetchall()) == 0:
            return 0
        else:
            last_update = self.cursor.execute("""SELECT update_time FROM update_logs WHERE rowid = ?""", (1,))
        self.connect.commit()
        return last_update.fetchall()[0][0]

    def close(self):
        """Закрытие соединений с БД"""
        self.connect.close()

# try:
#     connect = sqlite3.connect("F1Assistant.db")
#     cursor = connect.cursor()
#
#     # Создал год с year = 2022
#     cursor.execute("INSERT OR IGNORE INTO 'calendars_years' ('year') VALUES (?)", (2022,))
#
#     # Считываю все годы
#     years = cursor.execute("SELECT * FROM 'calendars_years'")
#     print(years.fetchall())
#
#     # Подтверждаем изменения
#     connect.commit()
#
# except sqlite3.Error as error:
#     print("Ошибка", error)
#
# finally:
#     if connect:
#         connect.close()