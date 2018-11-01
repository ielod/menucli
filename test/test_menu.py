import datetime
import mock
import unittest

import yaml

from menucli import menu


RESTAURANT = 'restaur'
EXAMPLE_RESTAURANT = {
    'name': RESTAURANT,
    'description': 'An example Restaurant near nowhere',
    'tag': 'FacebookRestaurID',
}

EXAMPLE_YAML_CONTENT = {'restaurants': [EXAMPLE_RESTAURANT]}

IN_ONELINE = True
IN_MULTILINE = False
SHORT = False
DETAILED = True

EXCEPTION_DUMMY_MESSAGE = 'Dummy Exception'
DUMMY_RESTAURANT = 'dummy restaurant'
DUMMY_SECTION = 'dummy section'
DUMMY_OPTION = 'dummy option'

EXAMPLE_MENU = '''some REAL mEnU

wITH FISH'''
EXAMPLE_MENU_PARSED = 'Some Real Menu\n\nWith Fish'
EXAMPLE_MENU_PARSED_ONELINE = 'Some Real Menu | With Fish'

EXAMPLE_EMPTY_JSON = {
    'data': [{
        'created_time': '',
        'message': ''
    }]
}
EXAMPLE_VALID_JSON = {
    'data': [{
        'created_time': datetime.date.today().strftime('%Y-%m-%dT00:00:00+0000'),
        'message': EXAMPLE_MENU
    }]
}


class TestMenuCLI(unittest.TestCase):

    def setUp(self):
        self.patch_rawconfig_parser = mock.patch('menucli.menu.configparser.RawConfigParser')
        self.mock_rawconfig_parser = self.patch_rawconfig_parser.start()
        self.patch_open = mock.patch('menucli.menu.open')
        self.mock_open = self.patch_open.start()
        self.patch_yaml = mock.patch('menucli.menu.yaml.load')
        self.mock_yaml = self.patch_yaml.start()
        self.patch_json = mock.patch('menucli.menu.json')
        self.mock_json = self.patch_json.start()
        self.patch_requests = mock.patch('menucli.menu.requests')
        self.mock_requests = self.patch_requests.start()

        self.mock_yaml.return_value = EXAMPLE_YAML_CONTENT

        self.menucli = menu.MenuCLI()

    def tearDown(self):
        self.patch_rawconfig_parser.stop()
        self.patch_open.stop()
        self.patch_yaml.stop()
        self.patch_json.stop()
        self.patch_requests.stop()

    def test_list_short(self):
        restaurant_list = self.menucli.list(SHORT)
        self.assertEqual(EXAMPLE_RESTAURANT['name'], restaurant_list)

    def test_list_detailed(self):
        restaurant_list = self.menucli.list(DETAILED)
        self.assertEqual('{:<10} : {}'.format(
            EXAMPLE_RESTAURANT['name'],
            EXAMPLE_RESTAURANT['description']),
            restaurant_list)

    def test_wrong_statuscode_from_response(self):
        fake_response = mock.Mock()
        fake_response.status_code = 404
        self.mock_requests.get.return_value = fake_response
        with self.assertRaises(menu.MenuException) as context:
            self.menucli.show(RESTAURANT, IN_ONELINE)
        self.assertEqual('Server response: 404',
                         str(context.exception))

    def test_show_menu_not_yet(self):
        fake_response = mock.Mock()
        fake_response.status_code = 200
        self.mock_requests.get.return_value = fake_response
        self.mock_json.loads.return_value = EXAMPLE_EMPTY_JSON

        todays_menu = self.menucli.show(RESTAURANT, IN_ONELINE)
        self.assertEqual('No menu for today... (yet?!) - {}'.format(EXAMPLE_RESTAURANT['tag']),
                         todays_menu)

    def test_show_oneline(self):
        fake_response = mock.Mock()
        fake_response.status_code = 200
        self.mock_requests.get.return_value = fake_response
        self.mock_json.loads.return_value = EXAMPLE_VALID_JSON

        todays_menu = self.menucli.show(RESTAURANT, IN_ONELINE)
        self.assertEqual(EXAMPLE_MENU_PARSED_ONELINE, todays_menu)

    def test_show_mutliple_line(self):
        fake_response = mock.Mock()
        fake_response.status_code = 200
        self.mock_requests.get.return_value = fake_response
        self.mock_json.loads.return_value = EXAMPLE_VALID_JSON

        todays_menu = self.menucli.show(RESTAURANT, IN_MULTILINE)
        self.assertEqual(EXAMPLE_MENU_PARSED, todays_menu)

    def test_show_no_such(self):
        with self.assertRaises(menu.MenuException) as context:
            self.menucli.show(DUMMY_RESTAURANT, IN_ONELINE)
        self.assertEqual('No such restaurant as {}'.format(DUMMY_RESTAURANT),
                         str(context.exception))

    def test_read_config_no_section(self):
        mock_config = mock.MagicMock()
        mock_config.get.side_effect = menu.NoSectionError(DUMMY_SECTION)
        self.mock_rawconfig_parser.return_value = mock_config
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._read_config()
        self.assertEqual('Config parsing failed... (Does {} exist?)'.format(menu.CONFIG_FILE),
                         str(context.exception))

    def test_read_config_no_option(self):
        mock_config = mock.MagicMock()
        mock_config.get.side_effect = menu.NoOptionError(DUMMY_OPTION, DUMMY_SECTION)
        self.mock_rawconfig_parser.return_value = mock_config
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._read_config()
        self.assertEqual("Config parsing failed... (No option '{}' in section: '{}')".format(
            DUMMY_OPTION, DUMMY_SECTION),
                         str(context.exception))

    def test_yaml_ioerror(self):
        self.mock_open.side_effect = IOError()
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._read_yaml()
        self.assertEqual('Restaurant list file not found: {}'.format(menu.YAML_FILE),
                         str(context.exception))

    def test_yaml_yamlerror(self):
        self.mock_yaml.side_effect = yaml.YAMLError(EXCEPTION_DUMMY_MESSAGE)
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._read_yaml()
        self.assertEqual('YAML load error: {}'.format(EXCEPTION_DUMMY_MESSAGE),
                         str(context.exception))

    def test_yaml_keyerror(self):
        self.mock_yaml.side_effect = KeyError()
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._read_yaml()
        self.assertEqual('Restaurants not found in YAML...'.format(EXCEPTION_DUMMY_MESSAGE),
                         str(context.exception))

    def test_empty_yaml(self):
        self.mock_yaml.return_value = {'restaurants': None}
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._read_yaml()
        self.assertEqual('0 entry in restaurant list...'.format(EXCEPTION_DUMMY_MESSAGE),
                         str(context.exception))

    def test_request_error(self):
        self.mock_requests.exceptions.ConnectionError = Exception
        self.mock_requests.get.side_effect = Exception(EXCEPTION_DUMMY_MESSAGE)
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._fetch_url(DUMMY_RESTAURANT)
        self.assertEqual(EXCEPTION_DUMMY_MESSAGE,
                         str(context.exception))

    def test_wrong_facebook_answer(self):
        fake_response = mock.Mock()
        fake_response.status_code = 200
        self.mock_requests.get.return_value = fake_response
        self.mock_json.loads.return_value = {}
        with self.assertRaises(menu.MenuException) as context:
            self.menucli._fetch_menu(DUMMY_RESTAURANT)
        self.assertEqual('Sorry, You have to look it by yourself: '
                         'https://www.facebook.com/{} :-/'.format(DUMMY_RESTAURANT),
                         str(context.exception))
