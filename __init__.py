# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


# Visit https://docs.mycroft.ai/skill.creation for more detailed information
# on the structure of this skill and its containing folder, as well as
# instructions for designing your own skill based on this template.

from os.path import dirname, exists, abspath, join
from os import mkdir, listdir

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft import MYCROFT_ROOT_PATH
# TODO consider http://pythonhosted.org/py-translate/index.html
from mtranslate import translate
import unicodedata

__author__ = 'jarbas'


class SkillTranslateSkill(MycroftSkill):
    def __init__(self):
        super(SkillTranslateSkill, self).__init__()
        self.skills_dir = abspath(dirname(dirname(__file__)))
        # TODO list of supported langs
        # NOTE check if google supports most lang codes
        self.unsupported_languages = []
        if self.validate_language():
            self.translate_skills()
            self.translate_core()

    def initialize(self):
        intent = IntentBuilder("AutoTranslateIntent"). \
            require("AutoTranslateKeyword").build()
        self.register_intent(intent, self.handle_intent)

    def validate_language(self):
        if self.lang not in self.unsupported_languages:
            return True
        return False

    def translate_skills(self):
        translated_skills = []
        for folder in listdir(self.skills_dir):
            folder_path = join(self.skills_dir, folder)
            dialog = join(folder_path, "vocab")
            en_dialog = join(dialog, "en-us")
            if exists(en_dialog):
                lang_folder = join(dialog, self.lang)
                if not exists(lang_folder):
                    mkdir(lang_folder)
                for dialog_file in listdir(en_dialog):
                    if ".dialog" in dialog_file:
                        translated_dialog = []
                        with open(join(en_dialog, dialog_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_dialog.append(self.translate(line))
                        with open(join(lang_folder, dialog_file), "w") as f:
                            f.writelines(translated_dialog)

            vocab = join(folder_path, "vocab")
            en_vocab = join(vocab, "en-us")
            if exists(en_vocab):
                lang_folder = join(vocab, self.lang)
                if not exists(lang_folder):
                    mkdir(lang_folder)
                for vocab_file in listdir(en_vocab):
                    if ".voc" in vocab_file:
                        translated_voc = []
                        with open(join(en_vocab, vocab_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_voc.append(self.translate(line))
                        with open(join(lang_folder, vocab_file), "w") as f:
                            f.writelines(translated_voc)

            regex = join(folder_path, "regex")
            en_regex = join(vocab, "en-us")
            if exists(en_regex):
                # TODO make sure regex keywords are not changed
                lang_folder = join(regex, self.lang)
                if not exists(lang_folder):
                    mkdir(lang_folder)
                for regex_file in listdir(en_regex):
                    if ".rx" in regex_file:
                        translated_regex = []
                        with open(join(en_regex, regex_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_regex.append(self.translate(line))
                        with open(join(lang_folder, regex_file), "w") as f:
                            f.writelines(translated_regex)

        return translated_skills

    def translate_core(self):
        dialog_path = join(MYCROFT_ROOT_PATH, "res", "dialog")
        en_dialog = join(dialog_path, "en-us")
        lang_dialog = join(dialog_path, self.lang)
        if not exists(en_dialog):
            return []
        translated = []
        if not exists(lang_dialog):
            mkdir(lang_dialog)
            for file in listdir(en_dialog):
                if ".dialog" in file and file not in listdir(lang_dialog):
                    with open(join(en_dialog, file), "r") as f:
                        lines = f.readlines()
                        for line in lines:
                            translated.append(self.translate(line))
                    with open(join(lang_dialog, file), "w") as f:
                        f.writelines(translated)

        return translated

    def translate(self, text):
        sentence = translate(text, self.lang)
        translated = unicodedata.normalize('NFKD', sentence).encode('ascii',
                                                                    'ignore')
        return translated

    def handle_intent(self, message):
        if self.validate_language():
            self.speak_dialog("translating_skills")
            if len(self.translate_core()):
                self.speak_dialog("translated_core")
            for skill in self.translate_skills():
                self.speak(skill)
        else:
            self.speak_dialog("invalid_language", {"language": self.lang})

    def stop(self):
        pass


def create_skill():
    return SkillTranslateSkill()
