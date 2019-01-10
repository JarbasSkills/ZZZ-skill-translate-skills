# Auto translate skill
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)](https://en.cryptobadges.io/donate/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/jarbasai)
<span class="badge-patreon"><a href="https://www.patreon.com/jarbasAI" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/JarbasAl)

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
