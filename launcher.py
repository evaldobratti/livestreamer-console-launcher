import requests
import livestreamer
import readline
import shlex
import os
import subprocess

def get_games():
	url = 'https://api.twitch.tv/kraken/games/top?limit=100'
	headers = {'Accept' : 'application/vnd.twitchtv.v3+json'}
	response = requests.get(url,headers=headers)
	if(response.status_code != requests.codes.ok):
		raise Exception()

	json_response = response.json()

	games = []
	for game in json_response['top']:
		games.append(game['game']['name'])

	return games

def get_streams(game):
	#print games

	url =  'https://api.twitch.tv/kraken/streams?game=' + game
	headers = {'Accept' : 'application/vnd.twitchtv.v3+json'}
	#print(url)
	response = requests.get(url,headers=headers)
	if (response.status_code != requests.codes.ok):
	    raise Exception()

	json_response = response.json()
	streams = []
	for stream in json_response['streams']:
	    streams.append((stream['channel']['display_name'],stream['channel']['url']))

	return streams

class Menu(object):
	def __init__(self, options, action, current_page=0):
		self.options = options
		self.action = action
		self.itens_per_page = 8
		self.current_page = current_page

	def show_options(self):
		start_index = self.current_page * self.itens_per_page
		final_index = start_index + self.itens_per_page
		for i, option in enumerate(self.options[start_index:final_index]):
			print str(i) + ' - ' + self.action.format(option)

		if len(self.options) > self.itens_per_page:
			print str(self.itens_per_page) + ' - next page'
			if self.current_page > 0:
				print str(self.itens_per_page + 1) + ' - previous page'

	def interprete(self, option):
		if option < self.itens_per_page:
			return self.action.advance(self.options[int(option)])

		if len(self.options) > self.itens_per_page:
			if option == self.itens_per_page:
				return Menu(self.options, self.action, self.current_page + 1)

			if option == (self.itens_per_page + 1) and self.current_page > 0:
				return Menu(self.options, self.action, self.current_page - 1)


class MenuAction(object):
	
	def advance(self, option):
		pass

	def format(self, option):
		return str(option)

class GameOption(MenuAction):
	
	def advance(self, option):
		return Menu(get_streams(option), StreamOption())


class StreamOption(MenuAction):
	
	def advance(self, option):
		qualities = livestreamer.streams(option[1])

		return Menu(zip(qualities.keys(), qualities.values()) , Execute())

	def format(self, option):
		return option[0]


class Execute(MenuAction):
	
	def advance(self, option):
		print option
		subprocess.call(['vlc',option[1].url])

	def format(self, option):
		return option[0]


if __name__ == '__main__':
	menu = Menu(get_games(), GameOption())

	while menu:
		menu.show_options()

		option = int(raw_input('> '))

		menu = menu.interprete(option)