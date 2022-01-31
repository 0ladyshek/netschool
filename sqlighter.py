import sqlite3
import ast
import secrets

class SQLighter:
	def __init__(self, db):
		self.connection = sqlite3.connect(db, check_same_thread=False)
		self.cursor = self.connection.cursor()
		self.cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY, account_id INT, token TEXT, accounts TEXT, notification INT);")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS accounts(account_id INT PRIMARY KEY,url TEXT, login TEXT, password TEXT, school INT, marks TEXT);")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS chats(chat_id INT PRIMARY KEY, account_id INT, moders TEXT, calls TEXT);")

	def user_exists(self, user_id = None, token = None):
		with self.connection:
			if user_id:
				result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
			else:
				result = self.cursor.execute("SELECT * FROM `users` WHERE `token` = ?", (token,)).fetchall()
			return bool(len(result))

	def account_exists(self, account_id):
		with self.connection:
			return bool(len(self.cursor.execute("SELECT * FROM `accounts` WHERE `account_id` = ?", (account_id,)).fetchall()))

	def chat_exists(self, chat_id):
		with self.connection:
			return bool(len(self.cursor.execute("SELECT * FROM `chats` WHERE `chat_id` = ?", (chat_id,)).fetchall()))

	def add_user(self, user_id, account_id = 0, token = secrets.token_hex(), accounts = '[]', notification = 0):
		with self.connection:
			return self.cursor.execute('INSERT INTO `users` (`user_id`, `account_id`, `token`, `accounts`, `notification`) VALUES(?,?,?,?,?)', (user_id, account_id, token, accounts, notification))

	def add_account(self, account_id, url, login, password, school, marks = '[]'):
		with self.connection:
			if not self.account_exists(account_id):
				return self.cursor.execute('INSERT INTO `accounts` (`account_id`, `url`, `login`, `password`, `school`, `marks`) VALUES(?,?,?,?,?,?)', (account_id, url, login, password, school, marks))

	def add_chat(self, chat_id, account_id = 0, moders = '[]', calls = None):
		with self.connection:
			return self.cursor.execute("INSERT INTO `chats` (`chat_id`, `account_id`, `moders`, `calls`) VALUES(?,?,?,?)", (chat_id, account_id, moders, calls))

	def add_moder(self, chat_id, moder):
		with self.connection:
			moders = ast.literal_eval(self.cursor.execute("SELECT `moders` FROM `chats` WHERE `chat_id` = ?", (chat_id,)).fetchall()[0][0])
			moders.append(moder)
			return self.cursor.execute("UPDATE `chats` SET `moders` = ? WHERE `chat_id` = ?", (str(moders), chat_id))

	def add_account_id(self, user_id, account_id):
		with self.connection:
			accounts = ast.literal_eval(self.cursor.execute("SELECT `accounts` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0])
			accounts.append(account_id)
			return self.cursor.execute("UPDATE `users` SET `accounts` = ? WHERE `user_id` = ?", (str(accounts), user_id))

	def get_account_id(self, user_id):
		with self.connection:
			return self.cursor.execute("SELECT `account_id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

	def get_token(self, user_id):
		with self.connection:
			return self.cursor.execute("SELECT `token` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

	def get_account_user(self, user_id = None, token = None):
		with self.connection:
			if token:
				return ast.literal_eval(self.cursor.execute("SELECT `accounts` FROM `users` WHERE `token` = ?", (token,)).fetchall()[0][0])
			return ast.literal_eval(self.cursor.execute("SELECT `accounts` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0])

	def get_account(self, account_id):
		with self.connection:
			return self.cursor.execute('SELECT * FROM `accounts` WHERE `account_id` = ?', (account_id,)).fetchall()[0]

	def get_moders(self, chat_id):
		with self.connection:
			return ast.literal_eval(self.cursor.execute("SELECT `moders` FROM `chats` WHERE `chat_id` = ?", (chat_id,)).fetchall()[0][0])

	def get_account_id_chat(self, chat_id):
		with self.connection:
			return self.cursor.execute("SELECT `account_id` FROM `chats` WHERE `chat_id` = ?", (chat_id,)).fetchall()[0][0]

	def get_calls(self, chat_id):
		with self.connection:
			return self.cursor.execute("SELECT `calls` FROM `chats` WHERE `chat_id` = ?", (chat_id,)).fetchall()[0][0]

	def get_notification_settings(self, user_id):
		with self.connection:
			return bool(self.cursor.execute("SELECT `notification` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0])

	def get_notification_users(self):
		with self.connection:
			return self.cursor.execute("SELECT * FROM `users` WHERE `notification` = ?", (1,)).fetchall()
	
	def edit_account_id(self, account_id, user_id):
		with self.connection:
			return self.cursor.execute('UPDATE `users` SET `account_id` = ? WHERE `user_id` = ?', (account_id, user_id))
	
	def edit_account_id_chat(self, chat_id, account_id = 0):
		with self.connection:
			return self.cursor.execute("UPDATE `chats` SET `account_id` = ? WHERE `chat_id` = ?", (account_id, chat_id))

	def edit_school(self, account_id, school):
		with self.connection:
			return self.cursor.execute("UPDATE `accounts` SET `school` = ? WHERE `account_id` = ?", (account_id, school))

	def edit_calls(self, chat_id, calls = ''):
		with self.connection:
			return self.cursor.execute("UPDATE `chats` SET `calls` = ? WHERE `chat_id` = ?", (calls, chat_id))

	def edit_marks(self, account_id, marks):
		with self.connection:
			return self.cursor.execute("UPDATE `accounts` SET `marks` = ? WHERE `account_id` = ?", (str(marks), account_id))

	def edit_notify(self, user_id, notify):
		with self.connection:
			return self.cursor.execute("UPDATE `users` SET `notification` = ? WHERE `user_id` = ?", (notify, user_id))

	def delete_account(self, account_id, user_id):
		with self.connection:
			accounts = self.get_account_user(user_id)
			accounts.remove(account_id)
			self.cursor.execute('UPDATE `users` SET `accounts` = ? WHERE `user_id` = ?', (str(accounts), user_id))
			return self.cursor.execute('UPDATE `users` SET `account_id` = ? WHERE `user_id` = ?', (0, user_id))

	def del_moder(self, chat_id, moder):
		with self.connection:
			moders = ast.literal_eval(self.cursor.execute("SELECT `moders` FROM `chats` WHERE `chat_id` = ?", (chat_id,)).fetchall()[0][0])
			moders.remove(moder)
			return self.cursor.execute("UPDATE `chats` SET `moders` = ? WHERE `chat_id` = ?", (str(moders), chat_id))