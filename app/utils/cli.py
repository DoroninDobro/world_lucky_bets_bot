# partially from https://github.com/aiogram/bot
import argparse

from app import config


def create_parser():
    arg_parser = argparse.ArgumentParser(prog=config.PROG_NAME, description=config.PROG_DESC, epilog=config.PROG_EP)
    arg_parser.add_argument('-p', '--polling', action='store_const', const=True, help=config.DESC_POLLING)
    arg_parser.add_argument('-s', '--skip-updates', action='store_const', const=True, help="Skip pending updates")
    return arg_parser


def cli():

    def polling(skip_updates: bool):
        """
        Start application
        """
        from app.utils.executor import runner

        runner.skip_updates = skip_updates
        runner.start_polling(reset_webhook=True)

    def webhook():
        """
        Run application in webhook mode
        """
        from app.utils.executor import runner
        runner.start_webhook(
            webhook_path=f'/{config.secret_str}/',

            host=config.LISTEN_IP,
            port=config.LISTEN_PORT,
        )

    from app import misc

    misc.setup()

    parser = create_parser()
    namespace = parser.parse_args()

    if namespace.polling:
        polling(namespace.skip_updates)
    else:
        webhook()
