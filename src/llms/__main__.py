import argparse
import sys

from llms import (
    create_brochure, simple_request, make_joke, battle_sim, add_config, list_config, interactive, chat_bot)

from helpers import view_user_conf

providers: [str] = ['-'] + view_user_conf()


def main() -> int:
    parser = argparse.ArgumentParser(prog='llms', usage='%(prog)s [options]')

    parser.add_argument('-p', '--provider', choices=providers, default='-', type=str, nargs="?",
                        help=f"provider to use.")
    parser.add_argument("-t", "--tone", type=str, nargs='?',
                        help="tone that the llm should respond with")

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    create_brochure_parser = subparsers.add_parser('createBrochure', help='create brochure using ai')
    create_brochure_parser.add_argument('url', type=str, default='', help="url to process")
    create_brochure_parser.set_defaults(func=create_brochure)

    simple_request_parser = subparsers.add_parser('simpleRequest', help="makes simple request to llm")
    simple_request_parser.add_argument("request", type=str, nargs='?')
    simple_request_parser.set_defaults(func=simple_request)

    make_joke_parser = subparsers.add_parser('makeJoke', help='makes joke using ai')
    make_joke_parser.add_argument("jokeType", type=str, default='sad', nargs="?")
    make_joke_parser.add_argument("audience", type=str, default='death', nargs="?")
    make_joke_parser.set_defaults(func=make_joke)

    battle_parser = subparsers.add_parser('battle', help='battle between different llms')
    battle_parser.add_argument("-f", "--firstMessage", type=str, default='Hello', nargs="?")
    battle_parser.add_argument("-nob", "--numberOfBattles", type=int, default=5, nargs="?")
    battle_parser.add_argument("-m", "--models", nargs="+", help=f"list of {providers}")
    battle_parser.set_defaults(func=battle_sim)

    add_config_parser = subparsers.add_parser('addConfig', help='add config to llm')
    add_config_parser.add_argument("file", type=str)
    add_config_parser.set_defaults(func=add_config)

    list_config_parser = subparsers.add_parser('listConfig', help='list llms configurations')
    list_config_parser.set_defaults(func=list_config)

    interactive_parser = subparsers.add_parser('interactive', help='use gradio to create interactive UI')
    interactive_parser.set_defaults(func=interactive)

    interactive_parser = subparsers.add_parser('chatBot', help='use gradio to create interactive chat bot')
    interactive_parser.set_defaults(func=chat_bot)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    sys.exit(main())
