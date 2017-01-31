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


__all__ = ("VulnerabilitySharedObj", )
