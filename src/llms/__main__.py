import sys

from helpers import Arguments, Config
from .main import create_brochure_using_ai


def main() -> int:
    args = Arguments().get_parser().parse_args()
    config = Config()

    if args.createBrochure:
        if not args.url:
            print("\nNo URL provided\n")
            sys.exit(1)
        create_brochure_using_ai(config, args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
