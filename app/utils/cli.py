# partially from https://github.com/aiogram/bot
import argparse

from loguru import logger

from app.constants import secret_str, LISTEN_IP, LISTEN_PORT, PROG_NAME, PROG_DESC, PROG_EP, DESC_POLLING
from app.misc import config as global_config


def create_parser():
    arg_parser = argparse.ArgumentParser(prog=PROG_NAME, description=PROG_DESC, epilog=PROG_EP)
    arg_parser.add_argument('-p', '--polling', action='store_const', const=True, help=DESC_POLLING)
    arg_parser.add_argument('-s', '--skip-updates', action='store_const', const=True, help="Skip pending updates")
    arg_parser.add_argument('-i', '--initialize', action='store_const', const=True,
                            help="create tables in db and exit")
    return arg_parser


def cli():

    def polling(skip_updates: bool):
        """
        Start application
        """
        from app.utils.executor import runner
        logger.info("starting polling...")

        runner.skip_updates = skip_updates
        runner.start_polling(reset_webhook=True)

    def webhook():
        """
        Run application in webhook mode
        """
        from app.utils.executor import runner
        logger.info("starting webhook...")
        runner.start_webhook(
            webhook_path=f'/{secret_str}/',

            host=LISTEN_IP,
            port=LISTEN_PORT,
        )

    from app.utils import log
    from app import misc

    log.setup(config=global_config)
    misc.setup(current_config=global_config)

    parser = create_parser()
    namespace = parser.parse_args()
    if namespace.initialize:
        from app.models.db.db import generate_schemas
        generate_schemas(global_config.db)
        return

    if namespace.polling:
        polling(namespace.skip_updates)
    else:
        webhook()
