import dbus
import os
import json
from urllib.parse import urlencode
import urllib.request as urlrequest
from time import sleep
import sys


class Spotify(object):

	def __init__(self, slack_channel):
		try:
			self.session_bus = dbus.SessionBus()
			self.spotify_bus = self.session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
			self.spotify_properties = dbus.Interface(self.spotify_bus, "org.freedesktop.DBus.Properties")
		except Exception as e:
			print("Spotify not running")
			exit()

		self.dir = os.path.dirname(os.path.realpath(__file__))
		self.preTextFile = self.dir + '/spotify.previous.song'

		if self.check_if_changed():
			song_name = self.set_current_song()
			print(song_name)
			slack = Slack(song_name)
			#slack.send_music(slack_channel)
			slack.set_status()

	def set_current_song(self):
		with open(self.preTextFile, 'w') as out:
			out.write(self.get_current_song())

		return self.get_current_song()

	def get_current_song(self):
		metadata = self.spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
		return metadata['xesam:title'] + ' - ' + metadata['xesam:artist'][0]

	def check_if_changed(self):
		return self.get_current_song() != self.get_previous_song()

	def get_previous_song(self):
		if not os.path.exists(self.preTextFile):
			return None

		return open(self.preTextFile, "r").read()

class Slack(object):
	def __init__(self, song, emoji = ':musical_note:'):
		self.url = ##WEBHOOK URL##
		self.opener = urlrequest.build_opener(urlrequest.HTTPHandler())
		self.song = song
		self.emoji = emoji

	def send_music(self, slack_channel):
		payload = urlencode({"payload": json.dumps({"channel": slack_channel, "text": self.song, "username": "Spotify Music", "icon_emoji": ":notes:"})})
		req = urlrequest.Request(self.url)
		response = self.opener.open(req, payload.encode('utf-8')).read()
		return response.decode('utf-8')

	def set_status(self):
		payload = urlencode({"token": ##TOKEN##, "profile": {"status_text": self.song, "status_emoji": self.emoji}})
		req = urlrequest.Request("https://slack.com/api/users.profile.set", payload.encode('utf-8'))
		urlrequest.urlopen(req)


if __name__ == '__main__':
	slack_channel = "@music"

	try:
		slack_channel = sys.argv[1]
	except: pass

	try:
		while True:
			Spotify(slack_channel)
			sleep(1)
	except (KeyboardInterrupt):
		Slack("What would the world be without lemons?!", ":lemon:").set_status()
		exit()
