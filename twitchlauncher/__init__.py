#!/usr/bin/python
import requests
import livestreamer
import readline
import shlex
import os
import subprocess
from menu import *

def get_games():
	url = 'https://api.twitch.tv/kraken/games/top?limit=100'
	headers = {'Accept' : 'application/vnd.twitchtv.v3+json'}
	response = requests.get(url,headers=headers)
	if(response.status_code != requests.codes.ok):
		raise Exception('It was not possible to retrieve online games, try again later.')

	json_response = response.json()

	return map(lambda x: x['game']['name'], json_response['top'])

def get_streams(game):
	url =  'https://api.twitch.tv/kraken/streams?limit=100&game=' + game
	headers = {'Accept' : 'application/vnd.twitchtv.v3+json'}
	
	response = requests.get(url,headers=headers)
	if (response.status_code != requests.codes.ok):
	    raise Exception('It was not possible to retrieve online streams for ' + game + ', try again later.')

	json_response = response.json()
	
	return json_response['streams']

def file_config_name():
	home = os.path.expanduser('~')
	basedir = os.path.join(home, '.twitchlauncher')

	if not os.path.exists(basedir):
		os.mkdir(basedir)

	return os.path.join(basedir, 'data.txt')

def save_stream_opened(last_opened):
	old_streams = load_saved()
	for old_stream in old_streams:
		if old_stream['channel']['name'] == last_opened['channel']['name']:
			old_streams.remove(old_stream)

	old_streams.insert(0, last_opened)

	with open(file_config_name(), 'w') as f:
		for stream in old_streams[0:10]:
			f.write(str(stream) + '\n')


def load_saved():
	streams = []
	with open(file_config_name(), 'a+') as f:
		for line in f:
			streams.append(eval(line))

	return streams


def update_data(stream):
	url =  'https://api.twitch.tv/kraken/streams/' + stream['channel']['name']
	headers = {'Accept' : 'application/vnd.twitchtv.v3+json'}
	
	response = requests.get(url,headers=headers)
	if (response.status_code != requests.codes.ok):
	    raise Exception()

	json_response = response.json()
	
	return json_response['stream']


class ShowFavorites(MenuAction):
	def advance(self, actual_menu):
		print 'Checking which stream is online, this may take a while...'
		streams = filter(lambda x: x is not None, map(update_data, load_saved()))

		return Menu(map(StreamOption, streams), previous=actual_menu)

	def format(self):
		return 'Last opened online'


class GameOption(MenuAction):
	def advance(self, actual_menu):
		return Menu(map(StreamOption, get_streams(self.option)), previous=actual_menu)


class StreamOption(MenuAction):
	def advance(self, actual_menu):
		qualities = livestreamer.streams(self.option['channel']['url'])
		save_stream_opened(self.option)
		return Menu(map(Execute, zip(qualities.keys(), qualities.values())), previous=actual_menu)

	def format(self):
		return 'Name: {:^20} - Lang: {:<3} - Viewers: {:>8} - Title: {}'.format(self.option['channel']['display_name'],
			self.option['channel']['language'], 
			self.option['viewers'],
			self.option['channel']['status'].encode("utf-8"))


class Execute(MenuAction):
	def advance(self, actual_menu):
		subprocess.call(['vlc',self.option[1].url])
		print 'Bye!'

	def format(self):
		return self.option[0]


def main():
	main_menu = [ShowFavorites()] + map(GameOption, get_games())
	menu = Menu(main_menu)

	while menu:
		menu.show_options()

		option = int(raw_input('> '))

		menu = menu.interprete(option)