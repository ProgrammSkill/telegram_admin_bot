import sqlite3

class BotDB:

    def __init__(self, db_file):
        # инициализация соеденения с БД
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def check_user(self, user_id):
        # проверка наличия администратора в базе данных
        result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def check_level(self, user_id):
        # вывод уровня администратора
        result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,))
        try:
            return int(result.fetchall()[0][2])
        except:
            return 0

    def add_user(self, user_id, level):
        # добавление администратора в БД
        self.cursor.execute("INSERT INTO `users` (`user_id`, `level`) VALUES (?, ?)", (user_id, level))
        return self.conn.commit()

    def change_level(self, user_id, level):
        # изменение уровня администратора
        self.cursor.execute("UPDATE `users` SET level = " + str(level) + " WHERE user_id = " + str(user_id))
        return self.conn.commit()

    def delete_user(self, user_id):
        # удаление пользователя
        self.cursor.execute("DELETE FROM `users` WHERE `user_id` = ?", (user_id,))
        return self.conn.commit()

    def list_administrators(self):
        # вывод списка администраторов
        result = self.cursor.execute("SELECT * FROM `users`")
        return result.fetchall()

    def close(self):
        # закрытие соединения с БД
        self.conn.close()