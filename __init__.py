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
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft import MYCROFT_ROOT_PATH
# TODO consider http://pythonhosted.org/py-translate/index.html
from mtranslate import translate
from mycroft.configuration.config import LocalConf, USER_CONFIG
import unicodedata
import re

__author__ = 'jarbas'


class SkillTranslateSkill(MycroftSkill):
    def __init__(self):
        super(SkillTranslateSkill, self).__init__()
        self.skills_dir = abspath(dirname(dirname(__file__)))
        self.reload_skill = False
        self.lang_map = {
            'af': 'Afrikaans',
            'sq': 'Albanian',
            'ar': 'Arabic',
            'hy': 'Armenian',
            'bn': 'Bengali',
            'ca': 'Catalan',
            'zh': 'Chinese',
            'zh-cn': 'Chinese (Mandarin/China)',
            'zh-tw': 'Chinese (Mandarin/Taiwan)',
            'zh-yue': 'Chinese (Cantonese)',
            'hr': 'Croatian',
            'cs': 'Czech',
            'da': 'Danish',
            'nl': 'Dutch',
            'en': 'English',
            'en-au': 'English (Australia)',
            'en-uk': 'English (United Kingdom)',
            'en-us': 'English (United States)',
            'eo': 'Esperanto',
            'fi': 'Finnish',
            'fr': 'French',
            'de': 'German',
            'el': 'Greek',
            'hi': 'Hindi',
            'hu': 'Hungarian',
            'is': 'Icelandic',
            'id': 'Indonesian',
            'it': 'Italian',
            'ja': 'Japanese',
            'km': 'Khmer (Cambodian)',
            'ko': 'Korean',
            'la': 'Latin',
            'lv': 'Latvian',
            'mk': 'Macedonian',
            'no': 'Norwegian',
            'pl': 'Polish',
            'pt': 'Portuguese',
            'ro': 'Romanian',
            'ru': 'Russian',
            'sr': 'Serbian',
            'si': 'Sinhala',
            'sk': 'Slovak',
            'es': 'Spanish',
            'es-es': 'Spanish (Spain)',
            'es-us': 'Spanish (United States)',
            'sw': 'Swahili',
            'sv': 'Swedish',
            'ta': 'Tamil',
            'th': 'Thai',
            'tr': 'Turkish',
            'uk': 'Ukrainian',
            'vi': 'Vietnamese',
            'cy': 'Welsh'
        }
        self.unsupported_languages = []
        self.full_translate_to(self.lang)

    def initialize(self):
        self.emitter.on("skills.auto_translate", self.translate_skills_dispatch)

    def translate_skills_dispatch(self, message):
        self.translate_skills()

    def full_translate_to(self, lang=None):
        ''' translate all skills to target language '''
        lang = lang or self.lang
        if self.validate_language(lang):
            self.log.info("Starting automatic translation")
            self.speak_to_dialogs()
            self.translate_skills(lang)
            self.translate_core(lang)
        else:
            self.log.info("Automatic translation not available for " + lang)

    def validate_language(self, lang=None):
        ''' ensure language is supported by google translate '''
        lang = lang or self.lang
        if lang not in self.unsupported_languages:
            if lang in self.lang_map:
                return True
            if lang[:2] in self.lang_map:
                return True
            for l in self.lang_map:
                if self.lang_map[l].lower() == lang.lower():
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
                if not exists(skill_path + ".backup"):
                    with open(skill_path + ".backup", "w") as b:
                        b.writelines(lines)
                for idx, line in enumerate(lines):
                    # get hardcoded speak text messages
                    tags = speak.findall(line)
                    # if " or ' in speak it is not a var, else filter
                    tags = [tag.replace("'", '').replace('"', "") for tag in
                            tags if ("'" in tag or '"' in tag)]
                    if not len(tags):
                        continue
                    # if some of these symbols is in the tag it is a string operation, leave it
                    symbols = ["+", "-", "/", "*", "[", "]", "(", ")"]
                    for s in symbols:
                        tags = [tag for tag in tags if s not in tag]
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

    def make_skills_auto_tx(self):
        for folder in listdir(self.skills_dir):
            # check if is a skill
            folder_path = join(self.skills_dir, folder)
            skill_path = join(folder_path, "__init__.py")
            if not exists(skill_path):
                return []
            with open(skill_path, "r") as f:
                skill = f.read()
                # save backup
                self.log.info("Saving backup of " + folder)
                if not exists(skill_path + ".autotx_backup"):
                    with open(skill_path + ".autotx_backup", "w") as b:
                        b.write(skill)
                if "MycroftSkill" not in skill:
                    # TODO fallbacks
                    continue
                skill = skill.replace("MycroftSkill", "AutotranslatableSkill")
                lines = skill.split("\n")
                for idx, line in enumerate(lines):
                    if line.startswith("#"):
                        continue
                    lines.insert(idx, "from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableSkill")
                    break
                lines.insert(0, "# skill auto translated ")
                skill = "".join(lines)
                with open(skill_path, "w") as b:
                    b.write(skill)
                reqs = join(folder_path, "requirements.txt")
                r = []
                if exists(reqs):
                    with open(reqs, "r") as b:
                        r = b.readlines()
                r.append("mycroft_jarbas_utils")
                with open(reqs, "w") as b:
                    b.writelines(r)

    def translate_skills(self, lang=None):
        ''' translate skills vocab/dialog/regex '''
        if lang is None:
            lang = self.lang
        translated_skills = []
        for folder in listdir(self.skills_dir):
            # check if is a skill
            folder_path = join(self.skills_dir, folder)
            skill_path = join(folder_path, "__init__.py")
            if not exists(skill_path):
                return []
            # translate dialogfiles
            dialog = join(folder_path, "dialog")
            en_dialog = join(dialog, "en-us")

            self.log.info("Translating dialog for " + folder)
            if exists(en_dialog):
                lang_folder = join(dialog, lang)
                if not exists(lang_folder):
                    self.log.info("Creating dialog language folder for " +
                                  lang)
                    mkdir(lang_folder)
                for dialog_file in listdir(en_dialog):
                    if ".dialog" in dialog_file and dialog_file not in \
                            listdir(lang_folder):
                        self.log.info("Translating " + dialog_file)
                        translated_dialog = []
                        with open(join(en_dialog, dialog_file), "r") as f:
                            lines = f.readlines()
                            original_tags = []
                            translated_tags = []
                            for line in lines:
                                original_tags += re.findall('\{\{[^}]*\}\}',
                                                            line)
                                translated = self.translate(line)+" \n"
                                translated_dialog.append(translated)
                                translated_tags += re.findall('\{\{[^}]*\}\}',
                                                              translated)
                                for idx, tag in enumerate(original_tags):
                                    for idr, line in enumerate(translated_dialog):
                                        try:
                                            # restore var names
                                            fixed = line.replace(translated_tags[idx],
                                                                    original_tags[idx].replace(" ", ""))
                                            words = fixed.split(" ")
                                            for i, w in enumerate(words):
                                                # translation randomly removes starting {{
                                                if "}}" in w and "{{" not in w:
                                                    words[i] = "{{"+w
                                                if "{{" in w and "}}" not in w:
                                                    words[i] += "}}"
                                            fixed = " ".join(words)
                                            translated_dialog[idr] = fixed
                                        except:
                                            self.log.error(dialog_file + " " \
                                                           "needs manual fixing")

                        with open(join(lang_folder, dialog_file), "w") as f:
                            f.writelines(translated_dialog)

            # translate vocab files
            self.log.info("Translating vocab for " + folder)
            vocab = join(folder_path, "vocab")
            en_vocab = join(vocab, "en-us")
            if exists(en_vocab):
                lang_folder = join(vocab, lang)
                if not exists(lang_folder):
                    self.log.info("Creating vocab language folder for " +
                                  lang)
                    mkdir(lang_folder)
                for vocab_file in listdir(en_vocab):
                    if ".voc" in vocab_file and vocab_file not in listdir(
                            lang_folder):
                        self.log.info("Translating " + vocab_file)
                        translated_voc = []
                        with open(join(en_vocab, vocab_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_voc.append(self.translate(
                                    line)+" \n")
                        with open(join(lang_folder, vocab_file), "w") as f:
                            f.writelines(translated_voc)

            # translate entity files
            self.log.info("Translating entities for " + folder)
            vocab = join(folder_path, "vocab")
            en_vocab = join(vocab, "en-us")
            if exists(en_vocab):
                lang_folder = join(vocab, lang)
                if not exists(lang_folder):
                    self.log.info("Creating vocab language folder for " +
                                  lang)
                    mkdir(lang_folder)
                for vocab_file in listdir(en_vocab):
                    if ".entity" in vocab_file and vocab_file not in listdir(
                            lang_folder):
                        self.log.info("Translating " + vocab_file)
                        translated_voc = []
                        with open(join(en_vocab, vocab_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_voc.append(self.translate(
                                    line) + " \n")
                        with open(join(lang_folder, vocab_file), "w") as f:
                            f.writelines(translated_voc)

            # translate intent files
            self.log.info("Translating intents for " + folder)
            vocab = join(folder_path, "vocab")
            en_vocab = join(vocab, "en-us")
            if exists(en_vocab):
                lang_folder = join(vocab, lang)
                if not exists(lang_folder):
                    self.log.info("Creating vocab language folder for " +
                                  lang)
                    mkdir(lang_folder)
                for vocab_file in listdir(en_vocab):
                    if ".intent" in vocab_file and vocab_file not in listdir(
                            lang_folder):
                        self.log.info("Translating " + vocab_file)
                        translated_voc = []
                        with open(join(en_vocab, vocab_file), "r") as f:
                            lines = f.readlines()
                            for line in lines:
                                translated_voc.append(self.translate(
                                    line) + " \n")
                        with open(join(lang_folder, vocab_file), "w") as f:
                            f.writelines(translated_voc)

            # TODO parse regex better, keywords must not be translated
            # translate regex
            self.log.info("Translating regex for " + folder)
            regex = join(folder_path, "regex")
            en_regex = join(regex, "en-us")
            if exists(en_regex):
                lang_folder = join(regex, lang)
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
                                translated_regex.append(self.translate(
                                    line)+" \n")
                        # restore regex vars
                        original_tags = []
                        translated_tags = []
                        parenthesis = []
                        for line in lines:
                            original_tags += re.findall('<[^>]*>', line)
                        for line in translated_regex:
                            translated_tags += re.findall('<[^>]*>', line)
                            parenthesis += re.findall('\([^)]*\)', line)
                        for idx, tag in enumerate(original_tags):
                            for idr, line in enumerate(translated_regex):
                                # fix spaces
                                for p in parenthesis:
                                    if p in line:
                                        line = line.replace(p, p.replace(" ",
                                                                         ""))
                                # restore var names
                                fixed = line.replace(translated_tags[idx],
                                                        original_tags[idx])

                                translated_regex[idr] = fixed

                        with open(join(lang_folder, regex_file), "w") as f:
                            f.writelines(translated_regex)

        return translated_skills

    def translate_core(self, lang=None):
        ''' translate core dialog files '''
        if lang is None:
            lang = self.lang
        dialog_path = join(MYCROFT_ROOT_PATH, "mycroft/res/text")
        en_dialog = join(dialog_path, "en-us")
        lang_dialog = join(dialog_path, lang)
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
                        translated.append(self.translate(line)+ " \n")
                with open(join(lang_dialog, file), "w") as f:
                    f.writelines(translated)
                self.log.debug(translated)
        return translated

    def translate(self, text, lang=None):
        ''' translate text to lang '''
        lang = lang or self.lang
        if lang[:2] in self.lang_map and lang not in self.lang_map:
            lang = lang[:2]
        elif lang not in self.lang_map:
            for l in self.lang_map:
                if self.lang_map[l].lower() == lang.lower():
                    lang = l
                    break
        sentence = translate(text, lang)
        translated = unicodedata.normalize('NFKD', sentence).encode('ascii',
                                                                    'ignore')
        return translated

    @intent_handler(IntentBuilder("AutoTranslateIntent"). \
            require("AutoTranslateKeyword"))
    def handle_auto_tx_intent(self, message):
        ''' translate yourself intent '''
        if self.validate_language():
            self.speak_dialog("translating_skills")
            if len(self.translate_core()):
                self.speak_dialog("translated_core")
            for skill in self.translate_skills():
                self.speak(skill)
        else:
            self.speak_dialog("invalid_language", {"language": self.lang})

    @intent_file_handler("translate_to.intent")
    def handle_auto_tx_to_lang_intent(self, message):
        lang = message.data.get("lang", self.lang)
        if self.validate_language(lang):
            self.speak_dialog("translating_skills")
            if len(self.translate_core()):
                self.speak_dialog("translated_core")
            for skill in self.translate_skills():
                self.speak(skill)
        else:
            self.speak_dialog("invalid_language", {"language": self.lang})

    @intent_handler(IntentBuilder("AutoTranslateSkillsIntent"). \
                    require("AutoTranslateSkillsKeyword"))
    def handle_auto_tx_skills_intent(self, message):
        ''' translate yourself intent '''
        self.make_skills_auto_tx()
        self.speak_dialog("auto_tx_skills")

    @intent_file_handler("change_lang_to.intent")
    def handle_change_lang_intent(self, message):
        lang = message.data.get("lang", self.lang)
        if self.validate_language(lang):
            if lang[:2] in self.lang_map and lang not in self.lang_map:
                lang = lang[:2]
            elif lang not in self.lang_map:
                for l in self.lang_map:
                    if self.lang_map[l].lower() == lang.lower():
                        lang = l
                        break
            lang_name = lang
            if lang_name in self.lang_map:
                lang_name = self.lang_map[lang_name]
            self.speak_dialog("new_lang", {"language": lang_name})
            conf = LocalConf(USER_CONFIG)
            conf['lang'] = lang
            conf.store()
            stt = self.config_core["stt"]
            stt["module"] = "google"
            if "google" not in stt:
                stt["google"] = {}
            if "credential" not in stt["google"]:
                stt["google"] = {"credential": {}}
            if "token" not in stt["google"]["credential"]:
                stt["google"]["credential"] = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
            conf["stt"] = "google"

            tts = self.config_core["tts"]
            tts["module"] = "google"
            conf["tts"] = tts
            self.emitter.emit(message.reply("mycroft.reboot"))
        else:
            self.speak_dialog("invalid_language", {"language": self.lang})


def create_skill():
    return SkillTranslateSkill()

