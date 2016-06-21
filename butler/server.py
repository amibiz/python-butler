from flask import Flask
from logbook import debug

try:
    from urlparse import urlparse
except ImportError:  # pragma: no cover
    from urllib.parse import urlparse  # pragma: no cover


class ButlerServer(object):
    """ButlerServer implements Butler functions in Flask application.

    ButlerServer create relevant routes and serve the application, following ButlerFunctions rules
    """

    def __init__(self, butler, url):
        """init all parameters.

        :param butler: Butler instance with the required functionality
        :param url: The URL to bind to the server
        """
        # create Flask application
        self._app = Flask(__name__)

        # register functions to app routes
        self.functions = butler.functions
        self._register_urls()

        # readurl params
        parsed_url = urlparse(url)
        self.host = parsed_url.hostname or '127.0.0.1'
        self.port = self._get_port_from_url(parsed_url)
        self.args = []
        self.kwargs = {}

    @staticmethod
    def _get_port_from_url(parsed_url):
        if parsed_url.port:
            return parsed_url.port
        if parsed_url.scheme == 'https':
            return 443
        return 80

    def _register_urls(self):
        """Read class functions and register the matching routes."""
        for function in self.functions:
            for url in function.get_urls():
                debug('Adding view {}, url {}'.format(function.name, url))
                self._app.add_url_rule(url, methods=[function.method], view_func=function.obj)

    def run(self, *args, **kwargs):
        """Start flask application, get all paramters as Flask.run method."""
        self._update_app_paramters(*args, **kwargs)
        self._app.run(host=self.host, port=self.port, *self.args, **self.kwargs)

    def _update_app_paramters(self, *args, **kwargs):
        """Parse `run` function parameters and updates `host` and `port` properties."""
        args = list(args)  # args is tuple, which is immutable
        try:
            self.host = args.pop(0)
            self.port = args.pop(0)
        except IndexError:
            pass
        if 'host' in kwargs:
            self.host = kwargs.pop('host')
        if 'port' in kwargs:
            self.port = kwargs.pop('port')

        # update old args and kwargs
        self.args = args + self.args[len(args):]
        self.kwargs.update(kwargs)
