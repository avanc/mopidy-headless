from __future__ import unicode_literals

import os

from mopidy import config, ext


__version__ = '0.0.1'


class Extension(ext.Extension):
    dist_name = 'Mopidy-Headless'
    ext_name = 'headless'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['volume_device'] = config.String()
        schema['volume_axis'] = config.String()
        schema['playlist_device'] = config.String()
        schema['playlist_axis'] = config.String()
        schema['mute_device'] = config.String()
        schema['mute_key'] = config.String()
        return schema

    def setup(self, registry):
        from .frontend import InputFrontend
        registry.add('frontend', InputFrontend)
