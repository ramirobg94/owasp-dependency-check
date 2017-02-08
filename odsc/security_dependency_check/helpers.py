from typing import List, Union


class odsc_plugin(object):
    def __init__(self, lang: Union[str, List[str]]):
        if not hasattr(lang, "append"):
            self.lang = [lang]
        else:
            self.lang = lang

    def __call__(self, f):
        f.odsc_plugin_enable = True
        f.odsc_plugin_lang = self.lang

        return f


__all__ = ("odsc_plugin", )
