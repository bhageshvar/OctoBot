import telegram
from telegram.ext import Updater  # , Dispatcher
import logging

from config.cst import *
from interfaces.telegram.bot import TelegramApp
from services.abstract_service import *
from tools.logging.logging_util import set_logging_level


class TelegramService(AbstractService):
    REQUIRED_CONFIG = {"chat-id": "", "token": ""}

    LOGGERS = ["telegram.bot", "telegram.ext.updater", "telegram.vendor.ptb_urllib3.urllib3.connectionpool"]

    def __init__(self):
        super().__init__()
        self.telegram_api = None
        self.chat_id = None
        self.telegram_app = None
        self.telegram_updater = None

    @staticmethod
    def is_setup_correctly(config):
        return CONFIG_TELEGRAM in config[CONFIG_CATEGORY_SERVICES] \
                and CONFIG_SERVICE_INSTANCE in config[CONFIG_CATEGORY_SERVICES][CONFIG_TELEGRAM]

    def prepare(self):
        if not self.telegram_api:
            self.chat_id = self.config[CONFIG_CATEGORY_SERVICES][CONFIG_TELEGRAM]["chat-id"]
            self.telegram_api = telegram.Bot(
                token=self.config[CONFIG_CATEGORY_SERVICES][CONFIG_TELEGRAM][CONFIG_TOKEN])

        if not self.telegram_app:
            if not self.telegram_updater:
                self.telegram_updater = Updater(
                    token=self.config[CONFIG_CATEGORY_SERVICES][CONFIG_TELEGRAM][CONFIG_TOKEN])

            if TelegramApp.is_enabled(self.config):
                self.telegram_app = TelegramApp(self.config, self, self.telegram_updater)

        set_logging_level(self.LOGGERS, logging.WARNING)

    def get_type(self):
        return CONFIG_TELEGRAM

    def get_endpoint(self):
        return self.telegram_api

    def get_updater(self):
        return self.telegram_updater

    def stop(self):
        if self.telegram_updater:
            # __exception_event.is_set()
            # self.telegram_updater.dispatcher.__stop_event.set()
            # self.telegram_updater.__exception_event.set()
            # self.telegram_updater.dispatcher.__exception_event.set()
            self.telegram_updater.dispatcher.running = False
            self.telegram_updater.running = False
            # self.telegram_updater.dispatcher.running = False
            # self.telegram_updater.stop()

    def has_required_configuration(self):
        return CONFIG_CATEGORY_SERVICES in self.config \
               and CONFIG_TELEGRAM in self.config[CONFIG_CATEGORY_SERVICES]  \
               and self.check_required_config(self.config[CONFIG_CATEGORY_SERVICES][CONFIG_TELEGRAM])

    def send_message(self, content):
        try:
            if content:
                self.telegram_api.send_message(chat_id=self.chat_id, text=content)
        except telegram.error.TimedOut:
            # retry on failing
            try:
                self.telegram_api.send_message(chat_id=self.chat_id, text=content)
            except telegram.error.TimedOut as e:
                self.logger.error(f"failed to send message : {e}")

    def _get_bot_url(self):
        return f"https://web.telegram.org/#/im?p={self.telegram_api.get_me().name}"

    def get_successful_startup_message(self):
        return f"Successfully initialized and accessible at: {self._get_bot_url()}."
