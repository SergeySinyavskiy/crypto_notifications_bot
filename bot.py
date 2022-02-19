import telebot
import requests
import datetime
from binance.client import Client
from apscheduler.schedulers.background import BlockingScheduler

bot_api = "TELEGRAM_BOT_API"
binance_api = 'BINANCE_API'
binance_secret = 'BINANCE_SECRET'
gas_api = 'https://ethgasstation.info/json/ethgasAPI.json'
notification_time = '00:00'

bot = telebot.TeleBot(bot_api)
client = Client(binance_api, binance_secret)
sched = BlockingScheduler()

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
	global notification_time
	notification_time = message.text
	bot.send_message(message.from_user.id, text='Notification time is set. You can start notifications by running the command [/run]')

@bot.message_handler(commands=['start'])
def process_notification_time(message):
	send = bot.send_message(message.from_user.id, text='Enter notification time(%H:%M):')
	bot.register_next_step_handler(send, get_time)
	
@bot.message_handler(commands=['run'])
def run_notifications(message):
	time = notification_time.split(':')
	bot.send_message(message.from_user.id, text='Notifications started.')
	print(time)
	sched.add_job(send_notification, 'cron', args=(message.from_user.id,), hour=time[0], minute=time[1])
	sched.start()

bot.polling(none_stop=True, interval=0)
