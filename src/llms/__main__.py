import argparse
import sys

from llms import create_brochure, simple_request, make_joke, add_config, list_config


def main() -> int:
    parser = argparse.ArgumentParser(prog='llms', usage='%(prog)s [options]')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    parser.add_argument("-p", "--provider", type=str,
                        help="provider to use. ex: -p app")
    parser.add_argument("-rcl", "--requestCharLimit", type=int, nargs='?',
                        help="limits the request size to the llm: default is 5000")
    parser.add_argument("-t", "--tone", type=str, nargs='?',
                        help="tone that the llm should respond with")

    create_brochure_parser = subparsers.add_parser('createBrochure', help='create brochure using ai')
    create_brochure_parser.set_defaults(func=create_brochure)
    create_brochure_parser.add_argument('--url', type=str, required=True, help="url to process")

    simple_request_parser = subparsers.add_parser('simpleRequest', help="makes simple request to llm")
    simple_request_parser.set_defaults(func=simple_request)
    simple_request_parser.add_argument("-r", "--request", type=str, nargs='?')

    make_joke_parser = subparsers.add_parser('makeJoke', help='makes joke using ai')
    make_joke_parser.set_defaults(func=make_joke)
    make_joke_parser.add_argument("-jt", "--jokeType", type=str, required=True)
    make_joke_parser.add_argument("-a", "--audience", type=str, required=True)

    add_config_parser = subparsers.add_parser('addConfig', help='add config to llm')
    add_config_parser.set_defaults(func=add_config)
    add_config_parser.add_argument("-f", "--file", type=str, required=True)

    list_config_parser = subparsers.add_parser('listConfig', help='list llms configurations')
    list_config_parser.set_defaults(func=list_config)

    args = parser.parse_args()
    args.func(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
