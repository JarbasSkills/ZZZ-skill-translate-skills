# Auto translate skill

Passive skill, checks current language and attempts auto translation:

    all skills vocab
    all skills dialog
    all skills regex
    core dialog files


Skills are parsed and all self.speak() messages converted to self.speak_dialog()

Original skill files are saved as __init__.py.backup

Triggered on every boot or with

    start automatic translation

Recommended to be made into a [Priority Skill][https://github.com/MycroftAI/mycroft-core/pull/1084]

Translated skills should be auto-reloaded

No files are overwritten if they already exist

# supported languages

https://translate.google.com/intl/en/about/languages/

# TODO

- translate yourself to "language" intent
- validate/convert language code before translating
- consider package pytranslate instead of mtranslate