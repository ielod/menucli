import mock
import unittest

from menucli import menu_cli


class TestMenuCLI(unittest.TestCase):

    def setUp(self):
        self.patch_argparser = mock.patch("menucli.menu_cli.argparse.ArgumentParser")
        self.mock_argparser = self.patch_argparser.start()
        self.patch_menu = mock.patch("menucli.menu.MenuCLI")
        self.mock_menu = self.patch_menu.start()

    def tearDown(self):
        self.patch_argparser.stop()
        self.patch_menu.stop()

    def test_show(self):
        mock_parsed_args = mock.MagicMock()
        mock_parsed_args.command = 'show'
        mock_parser = mock.MagicMock()
        mock_parser.parse_args.return_value = mock_parsed_args
        self.mock_argparser.return_value = mock_parser
        self.assertEqual(0, menu_cli.main())

    def test_list_with_exception(self):
        mock_parsed_args = mock.MagicMock()
        mock_parsed_args.command = 'list'
        mock_parser = mock.MagicMock()
        mock_parser.parse_args.return_value = mock_parsed_args
        self.mock_argparser.return_value = mock_parser
        mock_menu = mock.MagicMock()
        mock_menu.list.side_effect = menu_cli.menu.MenuException()
        self.mock_menu.return_value = mock_menu
        self.assertEqual(1, menu_cli.main())
