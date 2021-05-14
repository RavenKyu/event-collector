import argparse
import yaml

from event_collector.app.app import collector, app


def argument_parser():
    parser = argparse.ArgumentParser('data-collector')
    parser.add_argument('-a', '--address', default='localhost',
                        help='host address')
    parser.add_argument('-p', '--port', type=int, default=5001,
                        help='port')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-t', '--template_file', type=str, action='append')
    return parser


def main():
    parser = argument_parser()
    argspec = parser.parse_args()
    event_collector = collector

    if argspec.template_file:
        for t in argspec.template_file:
            with open(t, 'r') as f:
                schedules = yaml.safe_load(f)
            event_collector.add_events(schedules)

    app.run(host=argspec.address,
            port=argspec.port,
            debug=argspec.debug)


if __name__ == '__main__':
    main()
