class LoggerInterface(object):
    """Interface for logger classes"""

    def specialize_tag(self, tag):
        """
        Return a new class with logger interface.
        The child class will log all events to parent
        logger, save for the fact that each entry will
        have 'tag' added to list of tags.

        @param tag: tag that will be added to each entry
        @type tag: str
        @return: L{LoggerInterface} implementation instance
        """
        raise RuntimeError, 'abstract'

    def specialize_hierarchy(self, h):
        """
        Return a new class with logger interface.
        The child class will log all events to parent
        logger, save for the fact that each entry will
        have 'h' prepended to hierarchy (along with the
        needed dot - or not if logged hierarchy is empty)

        @param tag: tag that will be added to each entry
        @type tag: str
        @return: L{LoggerInterface} implementation instance        
        """
        raise RuntimeError, 'abstract'

    def log(self, *args, **kwargs):
        """
        Invoke appropriate LogEntry constructor with 
        *args and **kwargs.

        Relay the log onto suitable logging backend.
        """
        raise RuntimeError, 'abstract'        