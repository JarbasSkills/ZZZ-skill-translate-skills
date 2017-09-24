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
import re

__author__ = 'jarbas'


class SkillTranslateSkill(MycroftSkill):
    def __init__(self):
        super(SkillTranslateSkill, self).__init__()
        self.skills_dir = abspath(dirname(dirname(__file__)))
        # TODO list of supported langs
        # NOTE check if google supports most lang codes
        self.unsupported_languages = []
        self.full_translate_to(self.lang)

    def initialize(self):
        # TODO translate yourself to "lang" intent

        intent = IntentBuilder("AutoTranslateIntent"). \
            require("AutoTranslateKeyword").build()
        self.register_intent(intent, self.handle_intent)

    def full_translate_to(self, lang=None):
        ''' translate all skills to target language '''
        lang = lang or self.lang
        if self.validate_language(lang):
            self.log.info("Starting automatic translation")
            self.speak_to_dialogs()
            self.translate_skills()
            self.translate_core()
        else:
            self.log.info("Automatic translation not available for " + lang)

    def validate_language(self, lang=None):
        ''' ensure language is supported by google translate '''
        lang = lang or self.lang
        if lang not in self.unsupported_languages:
            return True
        return False

    def speak_to_dialogs(self):
        ''' convert all self.speak(text) to self.speak_dialog(text) ,
        save backup of original file '''
        for folder in listdir(self.skills_dir):
            folder_path = join(self.skills_dir, folder)
            skill_path = join(folder_path, "__init__.py")
            if not exists(skill_path):
                return []
            processed = []
            dialog = join(folder_path, "vocab")
            en_dialog = join(dialog, "en-us")
            # find self.speaks hardcoded
            save_flag = False
            speak = re.compile(r'self.speak\((?P<message>.*?)\)', re.UNICODE)
            with open(skill_path, "r") as f:
                lines = f.readlines()
                # save backup
                self.log.info("Saving backup of " + folder)
                if not exists(join(skill_path, ".backup")):
                    with open(join(skill_path, ".backup"), "w") as b:
                        b.writelines(lines)
                for idx, line in enumerate(lines):
                    # get hardcoded speak text messages
                    tags = speak.findall(line)
                    # if " or ' in speak it is not a var, else filter
                    tags = [tag.replace("'", '').replace('"', "") for tag in
                            tags if ("'" in tag or '"' in tag)]
                    if not len(tags):
                        continue
                    processed.append(tags)
                    self.log.info("Converting self.speak to "
                                  "self.speak_dialog")
                    for tag in tags:
                        # create dialog file
                        new_dialog = join(en_dialog, tag, ".dialog")
                        if not exists(new_dialog):
                            with open(new_dialog, "w") as f:
                                f.write(tag)
                        # replace speak with speak_dialog
                        line = line.replace("'", "").replace('"', "")
                        line = line.replace("self.speak(" + tag,
                                            "self.speak_dialog('" + tag + "'")
                        lines[idx] = line
                        save_flag = True
                        self.log.debug(line)
            # save updated
            if save_flag:
                self.log.info("Saving parsed skill " + folder_path)
                with open(skill_path, "w") as f:
                    f.writelines(lines)
            return processed

    def translate_skills(self):
        ''' translate skills vocab/dialog/regex '''
        translated_skills = []
        for folder in listdir(self.skills_dir):
            # check if is a skill
            folder_path = join(self.skills_dir, folder)
            skill_path = join(folder_path, "__init__.py")
            if not exists(skill_path):
                return []
            # translate dialogfiles
            dialog = join(folder_path, "vocab")
            en_dialog = join(dialog, "en-us")

            self.log.info("Translating dialog for " + folder)
            if exists(en_dialog):
                lang_folder = join(dialog, self.lang)
                if not exists(lang_folder):
                    mkdir(lang_folder)
                for dialog_file in listdir(en_dialog):
                    if ".dialog" in dialog_file and dialog_file not in \
                            listdir(lang_folder):
                        self.log.info("Translating " + dialog_file)
                        translated_dialog = []
                        with open(join(en_dialog, dialog_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_dialog.append(self.translate(line))
                        with open(join(lang_folder, dialog_file), "w") as f:
                            f.writelines(translated_dialog)
                        self.log.debug(translated_dialog)

            # translate vocab files
            self.log.info("Translating vocab for " + folder)
            vocab = join(folder_path, "vocab")
            en_vocab = join(vocab, "en-us")
            if exists(en_vocab):
                lang_folder = join(vocab, self.lang)
                if not exists(lang_folder):
                    mkdir(lang_folder)
                for vocab_file in listdir(en_vocab):
                    if ".voc" in vocab_file and vocab_file not in listdir(
                            lang_folder):
                        self.log.info("Translating " + vocab_file)
                        translated_voc = []
                        with open(join(en_vocab, vocab_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_voc.append(self.translate(line))
                        with open(join(lang_folder, vocab_file), "w") as f:
                            f.writelines(translated_voc)
                        self.log.debug(translated_voc)

            # TODO parse regex better, keywords must not be translated
            # translate regex
            self.log.info("Translating regex for " + folder)
            regex = join(folder_path, "regex")
            en_regex = join(regex, "en-us")
            if exists(en_regex):
                lang_folder = join(regex, self.lang)
                if not exists(lang_folder):
                    mkdir(lang_folder)
                for regex_file in listdir(en_regex):
                    if ".rx" in regex_file and regex_file not in listdir(
                            lang_folder):
                        self.log.info("Translating " + regex_file)
                        translated_regex = []
                        with open(join(en_regex, regex_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_regex.append(self.translate(line))
                        with open(join(lang_folder, regex_file), "w") as f:
                            f.writelines(translated_regex)
                        self.log.debug(translated_regex)

        return translated_skills

    def translate_core(self):
        ''' translate core dialog files '''
        dialog_path = join(MYCROFT_ROOT_PATH, "res", "dialog")
        en_dialog = join(dialog_path, "en-us")
        lang_dialog = join(dialog_path, self.lang)
        if not exists(en_dialog):
            return []
        translated = []
        if not exists(lang_dialog):
            mkdir(lang_dialog)
        self.log.info("Translating core dialog")
        for file in listdir(en_dialog):
            if ".dialog" in file and file not in listdir(lang_dialog):
                self.log.info("Translating " + file)
                with open(join(en_dialog, file), "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        translated.append(self.translate(line))
                with open(join(lang_dialog, file), "w") as f:
                    f.writelines(translated)
                self.log.debug(translated)
        return translated

    def translate(self, text, lang=None):
        ''' translate text to lang '''
        lang = lang or self.lang
        sentence = translate(text, lang)
        translated = unicodedata.normalize('NFKD', sentence).encode('ascii',
                                                                    'ignore')
        return translated

    def handle_intent(self, message):
        ''' translate yourself intent '''
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
