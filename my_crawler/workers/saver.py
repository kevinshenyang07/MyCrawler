# -*- coding: utf-8 -*-

import sys
import logging


class InvalidSaveConfigsError(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(InvalidSaveConfigsError, self).__init__(message)



class Saver(object):

    def __init__(self, save_configs=None):
        self._save_configs = save_configs
        return

    def attempt_save(self, url, item):
        """
        try to save result according to save configs
        """
        try:
            configs = self._save_configs
            if configs['type'] == 'file':
                self.save_to_file(url, item)
            elif configs['type'] == 'db':
                self.save_to_db()
            else:
                raise InvalidSaveConfigsError
        except InvalidSaveConfigsError:
            logging.error("invalid save configs, update 'save' field in the config.json")
        return


    async def save_to_file(self, url, item):
        """
        save the item to a file, must "try, except" and don't change the parameters and return
        :return status:
        """
        logging.debug("%r start: url=%r", self.__class__.__name__, url)

        try:
            configs = self._save_configs['save']
            write_path = configs['path']
            with open(write_path, 'a') as f:
                line = url + ": " + ", ".join(item) + '\n'
                f.write(line)
            status = 0

        # TODO: substitute to more specific exception
        except Exception as e:
            status = -1
            logging.error("%r error: %r, url=%r",
                          self.__class__.__name__, e, url)

        logging.debug("%r end: status=%r, url=%r",
                      self.__class__.__name__, status, url)
        return status


    async def save_to_db(self):
        """
        save the item to a database
        """
        raise NotImplementedError