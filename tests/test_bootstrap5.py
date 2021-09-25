import pytest
from flask import current_app
from flask_bootstrap import CDN_BASE


@pytest.mark.usefixtures('client')
class TestBootstrap5:
    def test_extension_init(self, bootstrap5):
        assert 'bootstrap' in current_app.extensions

    def test_load_css_with_default_versions(self, bootstrap5):
        rv = bootstrap5.load_css()
        bootstrap_css = f'<link rel="stylesheet" href="{CDN_BASE}/bootstrap@{bootstrap5.bootstrap_version}/' \
                        f'dist/css/bootstrap.min.css" integrity="{bootstrap5.bootstrap_css_integrity}" ' \
                        'crossorigin="anonymous">'
        assert bootstrap_css in rv

    def test_load_css_with_non_default_versions(self, bootstrap5):
        def _check_assertions(rv):
            assert 'bootstrap.min.css' in rv
            assert 'integrity="' not in rv
            assert 'crossorigin="anonymous"' not in rv

        rv = bootstrap5.load_css(version='5.5.6')
        _check_assertions(rv)
        rv = bootstrap5.load_css(version='5.0.0')
        _check_assertions(rv)

    def test_load_js_with_default_versions(self, bootstrap5):
        rv = bootstrap5.load_js()
        bootstrap_js = f'<script src="{CDN_BASE}/bootstrap@{bootstrap5.bootstrap_version}/dist/js/' \
                       f'bootstrap.min.js" integrity="{bootstrap5.bootstrap_js_integrity}" ' \
                       'crossorigin="anonymous"></script>'
        jquery_js = f'<script src="{CDN_BASE}/jquery@{bootstrap5.jquery_version}/dist/jquery.min.js"' \
                    f' integrity="{bootstrap5.jquery_integrity}" crossorigin="anonymous"></script>'
        popper_js = f'<script src="{CDN_BASE}/popper.js@{bootstrap5.popper_version}/dist/umd/popper.min.js"' \
                    f' integrity="{bootstrap5.popper_integrity}" crossorigin="anonymous"></script>'
        assert bootstrap_js in rv
        assert jquery_js not in rv
        assert popper_js in rv

    def test_load_js_with_non_default_versions(self, bootstrap5):
        def _check_assertions(rv):
            assert 'bootstrap.min.js' in rv
            assert 'jquery.min.js' not in rv
            assert 'popper.min.js' in rv
            assert 'integrity="' not in rv
            assert 'crossorigin="anonymous"' not in rv

        rv = bootstrap5.load_js(version='5.5.6', popper_version='4.5.6')
        _check_assertions(rv)
        rv = bootstrap5.load_js(version='5.0.0', popper_version='4.0.0')
        _check_assertions(rv)

    def test_local_resources(self, bootstrap5, client):
        current_app.config['BOOTSTRAP_SERVE_LOCAL'] = True

        response = client.get('/')
        data = response.get_data(as_text=True)
        assert f'{CDN_BASE}/bootstrap' not in data
        assert 'bootstrap.min.js' in data
        assert 'bootstrap.min.css' in data
        assert 'jquery.min.js' not in data
        assert 'integrity="' not in data
        assert 'crossorigin="anonymous"' not in data

        with client.get('/bootstrap/static/css/bootstrap.min.css') as css_response:
            assert css_response.status_code != 404
        with client.get('/bootstrap/static/js/bootstrap.min.js') as js_response:
            assert js_response.status_code != 404
        with client.get('/bootstrap/static/jquery.min.js') as jquery_response:
            assert jquery_response.status_code == 404

        css_rv = bootstrap5.load_css()
        js_rv = bootstrap5.load_js()
        assert '/bootstrap/static/css/bootstrap.min.css' in css_rv
        assert '/bootstrap/static/js/bootstrap.min.js' in js_rv
        assert f'{CDN_BASE}/bootstrap' not in css_rv
        assert f'{CDN_BASE}/bootstrap' not in js_rv
        assert 'integrity="' not in css_rv
        assert 'crossorigin="anonymous"' not in css_rv
        assert 'integrity="' not in js_rv
        assert 'crossorigin="anonymous"' not in js_rv
