from typing import List, Union


class VulnerabilitySharedObj:

    def __init__(self, library, version, severity, summary, advisory):
        self.library = library
        self.version = version
        self.severity = severity
        self.summary = summary
        self.advisory = advisory

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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


__all__ = ("VulnerabilitySharedObj", "odsc_plugin")
