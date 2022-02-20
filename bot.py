import telebot
import requests
import datetime
from binance.client import Client
from apscheduler.schedulers.background import BlockingScheduler

bot_api = "TELEGRAM_BOT_API"
binance_api = 'BINANCE_API'
binance_secret = 'BINANCE_SECRET'
gas_api = 'https://ethgasstation.info/json/ethgasAPI.json'
notifications_time = []

bot = telebot.TeleBot(bot_api)
client = Client(binance_api, binance_secret)
sched = BlockingScheduler(timezone="Europe/Kiev")

def get_tickers():
	return {i: float(client.get_symbol_ticker(symbol=i+"USDT")["price"]) for i in ['BTC', 'ETH', 'BNB']}

def get_gas_price():
	r = requests.get(gas_api)
	return round(r.json()["average"] / 10)

def send_notification(id):
	tickers = get_tickers()
	gas_price = get_gas_price()
	text = 'Scheduled crypto notification:\n'
	prices = '\n'.join(f'{i}: {tickers[i]}$' for i in tickers)
	gas = f'\nEther gas price: {gas_price} gwei'
	res = text + prices + gas
	print(res)
	bot.send_message(id, text=res)

def get_time(message):
	global notifications_time
	notifications_time.append(message.text)
	bot.send_message(message.from_user.id, text='Notification added. Add more notifications or run having by running the command [/run]')

@bot.message_handler(commands=['start'])
def process_notification_time(message):
	bot.send_message(message.from_user.id, text='Welcome to crypto notifications bot. Press [/add] to add new notification time.')

@bot.message_handler(commands=['add'])
def add_notification(message):
	send = bot.send_message(message.from_user.id, text='Enter notification time(%H:%M):')
	bot.register_next_step_handler(send, get_time)

@bot.message_handler(commands=['stop'])
def stop_notifications(message):
	pass
	# TODO: Add method to remove the jobs

@bot.message_handler(commands=['run'])
def run_notification(message):
	bot.send_message(message.from_user.id, text='Notifications started.')
	for i in notifications_time:
		time = i.split(':')
		sched.add_job(send_notification, 'cron', args=(message.from_user.id,), hour=time[0], minute=time[1])
	sched.start()

bot.polling(none_stop=True, interval=0)
