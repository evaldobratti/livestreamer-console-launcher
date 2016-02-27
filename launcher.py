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
	url =  'https://api.twitch.tv/kraken/streams?game=' + game
	headers = {'Accept' : 'application/vnd.twitchtv.v3+json'}
	
	response = requests.get(url,headers=headers)
	if (response.status_code != requests.codes.ok):
	    raise Exception()

	json_response = response.json()
	streams = []
	for stream in json_response['streams']:
	    streams.append((stream['channel']['display_name'],stream['channel']['url']))

	return streams

class Menu(object):
	def __init__(self, options, page=0, previous=None):
		self.options = options
		self.itens_per_page = 8
		self.current_page = page
		self.previous = previous

		start_index = self.current_page * self.itens_per_page
		final_index = start_index + self.itens_per_page
		self.current_options = self.options[start_index:final_index]

		if len(self.options) > self.itens_per_page:
			self.current_options.append(NextPage(self))

		if self.current_page > 0:
			self.current_options.append(PreviousPage(self))

		if self.previous:
			self.current_options.append(Return(self.previous))

	
	def show_options(self):
		self.current_options.append(Exit(None))

		for i, option in enumerate(self.current_options):
			print str(i) + ' - ' + option.format()


	def interprete(self, option):
		return self.current_options[option].advance(self)
		

class MenuAction(object):
	
	def __init__(self, option):
		self.option = option

	def advance(self, actual_menu):
		pass

	def format(self):
		return str(self.option)

class GameOption(MenuAction):
	def advance(self, actual_menu):
		return Menu(map(StreamOption, get_streams(self.option)), previous=actual_menu)


class StreamOption(MenuAction):
	def advance(self, actual_menu):
		qualities = livestreamer.streams(self.option[1])

		return Menu(map(Execute, zip(qualities.keys(), qualities.values())), previous=actual_menu)

	def format(self):
		return self.option[0]


class Execute(MenuAction):
	def advance(self, actual_menu):
		subprocess.call(['vlc',self.option[1].url])

	def format(self):
		return self.option[0]

class NextPage(MenuAction):
	def advance(self, actual_menu):
		return Menu(self.option.options, self.option.current_page + 1, previous=self.option.previous)

	def format(self):
		return 'next page'

class PreviousPage(MenuAction):
	def advance(self, actual_menu):
		return Menu(self.option.options, self.option.current_page - 1, previous=self.option.previous)

	def format(self):
		return 'previous page'

class Return(MenuAction):
	def advance(self, actual_menu):
		return Menu(self.option.options, previous=self.option.previous)

	def format(self):
		return 'return'

class Exit(MenuAction):
	def advance(self, actual_menu):
		return None

	def format(self):
		return 'exit'

class Blah(MenuAction):
	def advance(self, actual_menu):
		return Menu([Blah(1),Blah(2)], previous = actual_menu)

	def format(self):
		return 'lel'

if __name__ == '__main__':
	main_menu = [ Blah(None) ] + map(GameOption, get_games())
	menu = Menu(main_menu)

	while menu:
		menu.show_options()

		option = int(raw_input('> '))

		menu = menu.interprete(option)