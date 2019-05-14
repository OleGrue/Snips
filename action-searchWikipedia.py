#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import io
import sys

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import wikipedia as wiki

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """

    :param hermes:
    :param intentMessage:
    :param conf:
    :return:
    """
    if len(intentMessage.slots.article_indicator) > 0:
        article = intentMessage.slots.article_indicator.first().value
        wiki.set_lang('de')
        try:
            results = wiki.search(article, 5)
            lines = 2
            summary = wiki.summary(results[0], lines)
            if "==" in summary or len(summary) > 250:
                # We hit the end of the article summary or hit a really long
                # one.  Reduce to first line.
                lines = 1
                summary = wiki.summary(results[0], lines)

            summary = re.sub(r'\([^)]*\)|/[^/]*/', '', summary).encode('utf8')
            hermes.publish_end_session(intentMessage.session_id, summary)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            hermes.publish_end_session(intentMessage.session_id, "An error occured")
    else:
        hermes.publish_end_session(intentMessage.session_id, "An error occured")



if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("CrystalMethod:searchWikipedia", subscribe_intent_callback) \
         .start()
