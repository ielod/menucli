import configparser
from configparser import NoSectionError
from configparser import NoOptionError
import datetime
import os
import re

import json
import yaml
import requests


CONFIG_FILE = '~/.config/menucli/menucli.cfg'
YAML_FILE = '~/.config/menucli/restaurants.yaml'
URL = 'https://graph.facebook.com/{}/feed?limit=3&access_token={}|{}'


class MenuException(Exception):
    pass


class MenuCLI:

    def __init__(self):
        self.app_id, self.app_token = self._read_config()
        self.restaurants = self._read_yaml()
        self.restaurant_tags = {}
        for restaurant in self.restaurants:
            self.restaurant_tags[restaurant['name']] = restaurant['tag']
        self.oneline = False

    @staticmethod
    def _read_config():
        app_id = None
        app_token = None
        try:
            config = configparser.RawConfigParser()
            config.read(os.path.expanduser(CONFIG_FILE))
            app_id = config.get('MenuCLI', 'app_id')
            app_token = config.get('MenuCLI', 'app_token')
        except NoSectionError:
            raise MenuException('Config parsing failed... (Does {} exist?)'.format(CONFIG_FILE))
        except NoOptionError as exc:
            raise MenuException('Config parsing failed... ({})'.format(str(exc)))
        return app_id, app_token

    @staticmethod
    def _read_yaml():
        restaurant_yaml = None
        try:
            with open(os.path.expanduser(YAML_FILE), 'r') as yaml_file:
                try:
                    restaurant_yaml = yaml.load(yaml_file)['restaurants']
                except yaml.YAMLError as exc:
                    raise MenuException('YAML load error: {}'.format(exc))
                except (KeyError, TypeError):
                    raise MenuException('Restaurants not found in YAML...')
        except IOError:
            raise MenuException('Restaurant list file not found: {}'.format(YAML_FILE))
        if restaurant_yaml is None:
            raise MenuException('0 entry in restaurant list...')
        return restaurant_yaml

    def _format_todays_offer(self, message):
        message = message.title()
        if self.oneline:
            todays_offer = ' '.join(' | '.join(message.split('\n')).split())
            todays_offer = re.sub(r'\|( \|)+', '|', todays_offer)
        else:
            todays_offer = message
        return todays_offer

    def _fetch_url(self, restaurant):
        try:
            response = requests.get(URL.format(restaurant, self.app_id, self.app_token))
        except requests.exceptions.ConnectionError as exc:
            raise MenuException(str(exc))
        if response.status_code == 200:
            return json.loads(response.content)
        raise MenuException("Server response: {}".format(response.status_code))

    def _fetch_menu(self, restaurant):
        fetched_data = self._fetch_url(restaurant)
        today = datetime.date.today().strftime("%Y-%m-%dT00:00:00+0000")
        todays_offer = None
        try:
            for item in fetched_data['data']:
                if item['created_time'] >= today and 'message' in item:
                    todays_offer = self._format_todays_offer(item['message'])
        except Exception:
            # print(fetched_data)
            # print('Exception happened: {}\n'.format(str(exc)))
            raise MenuException('Sorry, You have to look it by yourself: '
                                'https://www.facebook.com/{} :-/'.format(restaurant))
        if todays_offer is None:
            return 'No menu for today... (yet?!) - {}'.format(restaurant)
        return todays_offer

    def show(self, restaurant, oneline):
        self.oneline = oneline
        if restaurant in self.restaurant_tags:
            menu = self._fetch_menu(self.restaurant_tags[restaurant])
        else:
            raise MenuException('No such restaurant as {}'.format(restaurant))
        return menu

    def list(self, detailed):
        restaurant_list = ''
        for restaurant in self.restaurants:
            if detailed:
                restaurant_list += '{:<10} : {}\n'.format(restaurant['name'], restaurant['description'])
            else:
                restaurant_list += '{}, '.format(restaurant['name'])
        return restaurant_list.strip().strip(',')
