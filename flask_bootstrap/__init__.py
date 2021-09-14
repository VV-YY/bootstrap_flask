# -*- coding: utf-8 -*-
"""
    flask_bootstrap
    ~~~~~~~~~~~~~~
    :copyright: (c) 2017 by Grey Li.
    :license: MIT, see LICENSE for more details.
"""
import warnings

from flask import current_app, Markup, Blueprint, url_for

try:  # pragma: no cover
    from wtforms.fields import HiddenField
except ImportError:
    def is_hidden_field_filter(field):
        raise RuntimeError('WTForms is not installed.')
else:
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

# central definition of used versions and SRI hashes
VERSION_BOOTSTRAP = '4.3.1'
VERSION_JQUERY = '3.4.1'
VERSION_POPPER = '1.14.0'
BOOTSTRAP_CSS_INTEGRITY = 'sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T'
BOOTSTRAP_JS_INTEGRITY = 'sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM'
JQUERY_INTEGRITY = 'sha384-vk5WoKIaW/vJyUAd9n/wmopsmNhiy+L2Z+SBxGYnUkunIxVxAv/UtMOhba/xskxh'
POPPER_INTEGRITY = 'sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ'
CDN_BASE = 'https://cdn.jsdelivr.net/npm'


def raise_helper(message):  # pragma: no cover
    raise RuntimeError(message)


def get_table_titles(data, primary_key, primary_key_title):
    """Detect and build the table titles tuple from ORM object, currently only support SQLAlchemy.

    .. versionadded:: 1.4.0
    """
    if not data:
        return []
    titles = []
    for k in data[0].__table__.columns.keys():
        if not k.startswith('_'):
            titles.append((k, k.replace('_', ' ').title()))
    titles[0] = (primary_key, primary_key_title)
    return titles


class Bootstrap(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['bootstrap'] = self

        blueprint = Blueprint('bootstrap', __name__, static_folder='static',
                              static_url_path=f'/bootstrap{app.static_url_path}',
                              template_folder='templates')
        app.register_blueprint(blueprint)

        app.jinja_env.globals['bootstrap'] = self
        app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter
        app.jinja_env.globals['get_table_titles'] = get_table_titles
        app.jinja_env.globals['warn'] = warnings.warn
        app.jinja_env.globals['raise'] = raise_helper
        app.jinja_env.add_extension('jinja2.ext.do')
        # default settings
        app.config.setdefault('BOOTSTRAP_SERVE_LOCAL', False)
        app.config.setdefault('BOOTSTRAP_BTN_STYLE', 'primary')
        app.config.setdefault('BOOTSTRAP_BTN_SIZE', 'md')
        app.config.setdefault('BOOTSTRAP_BOOTSWATCH_THEME', None)
        app.config.setdefault('BOOTSTRAP_ICON_SIZE', '1em')
        app.config.setdefault('BOOTSTRAP_ICON_COLOR', None)
        app.config.setdefault('BOOTSTRAP_MSG_CATEGORY', 'primary')
        app.config.setdefault('BOOTSTRAP_TABLE_VIEW_TITLE', 'View')
        app.config.setdefault('BOOTSTRAP_TABLE_EDIT_TITLE', 'Edit')
        app.config.setdefault('BOOTSTRAP_TABLE_DELETE_TITLE', 'Delete')
        app.config.setdefault('BOOTSTRAP_TABLE_NEW_TITLE', 'New')

    @staticmethod
    def load_css(version=VERSION_BOOTSTRAP, bootstrap_sri=None):
        """Load Bootstrap's css resources with given version.

        .. versionadded:: 0.1.0

        :param version: The version of Bootstrap.
        """
        css_filename = 'bootstrap.min.css'
        serve_local = current_app.config['BOOTSTRAP_SERVE_LOCAL']
        bootswatch_theme = current_app.config['BOOTSTRAP_BOOTSWATCH_THEME']

        if version == VERSION_BOOTSTRAP and serve_local is False and bootstrap_sri is None:
            bootstrap_sri = BOOTSTRAP_CSS_INTEGRITY

        if serve_local:
            if not bootswatch_theme:
                base_path = 'css/'
            else:
                base_path = f'css/swatch/{bootswatch_theme.lower()}/'
            boostrap_url = url_for('bootstrap.static', filename=f'{base_path}{css_filename}')
        else:
            if bootswatch_theme:
                boostrap_url = f'{CDN_BASE}/bootswatch@{version}/dist/{bootswatch_theme.lower()}/{css_filename}'
            else:
                boostrap_url = f'{CDN_BASE}/bootstrap@{version}/dist/css/{css_filename}'

        if bootstrap_sri and not bootswatch_theme:
            css = f'<link rel="stylesheet" href="{boostrap_url}" integrity="{bootstrap_sri}" crossorigin="anonymous">'
        else:
            css = f'<link rel="stylesheet" href="{boostrap_url}">'
        return Markup(css)

    @staticmethod
    def load_js(version=VERSION_BOOTSTRAP, jquery_version=VERSION_JQUERY,  # noqa: C901
                popper_version=VERSION_POPPER, with_jquery=True, with_popper=True,
                bootstrap_sri=None, jquery_sri=None, popper_sri=None):
        """Load Bootstrap and related library's js resources with given version.

        .. versionadded:: 0.1.0

        :param version: The version of Bootstrap.
        :param jquery_version: The version of jQuery.
        :param popper_version: The version of Popper.js.
        :param with_jquery: Include jQuery or not.
        :param with_popper: Include Popper.js or not.
        """
        bootstrap_filename = 'bootstrap.min.js'
        jquery_filename = 'jquery.min.js'
        popper_filename = 'popper.min.js'

        serve_local = current_app.config['BOOTSTRAP_SERVE_LOCAL']

        if version == VERSION_BOOTSTRAP and serve_local is False and bootstrap_sri is None:
            bootstrap_sri = BOOTSTRAP_JS_INTEGRITY
        if jquery_version == VERSION_JQUERY and serve_local is False and jquery_sri is None:
            jquery_sri = JQUERY_INTEGRITY
        if popper_version == VERSION_POPPER and serve_local is False and popper_sri is None:
            popper_sri = POPPER_INTEGRITY

        if serve_local:
            bootstrap_url = url_for('bootstrap.static', filename=f'js/{bootstrap_filename}')
        else:
            bootstrap_url = f'{CDN_BASE}/bootstrap@{version}/dist/js/{bootstrap_filename}'
        if bootstrap_sri:
            bootstrap = f'<script src="{bootstrap_url}" integrity="{bootstrap_sri}" crossorigin="anonymous"></script>'
        else:
            bootstrap = f'<script src="{bootstrap_url}"></script>'

        if with_jquery:
            if serve_local:
                jquery_url = url_for('bootstrap.static', filename=jquery_filename)
            else:
                jquery_url = f'{CDN_BASE}/jquery@{jquery_version}/dist/{jquery_filename}'
            if jquery_sri:
                jquery = f'<script src="{jquery_url}" integrity="{jquery_sri}" crossorigin="anonymous"></script>'
            else:
                jquery = f'<script src="{jquery_url}"></script>'
        else:
            jquery = ''

        if with_popper:
            if serve_local:
                popper_url = url_for('bootstrap.static', filename=popper_filename)
            else:
                popper_url = f'{CDN_BASE}/popper.js@{popper_version}/dist/umd/{popper_filename}'
            if popper_sri:
                popper = f'<script src="{popper_url}" integrity="{popper_sri}" crossorigin="anonymous"></script>'
            else:
                popper = f'<script src="{popper_url}"></script>'
        else:
            popper = ''
        return Markup(f'''{jquery}
    {popper}
    {bootstrap}''')
