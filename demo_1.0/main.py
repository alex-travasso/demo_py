import json
import logging

from flask import Flask, g
from flask_oidc import OpenIDConnect

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'HXhuNd9xBamc8ORvP3PUGyODVfFThX8_yPfgqohOXio',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets_GOO.json',
    'OIDC_SCOPES': ['openid', 'phone', 'profile', 'email'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_OPENID_REALM': 'https://mid-dev.com/oidc_callback'
})
oidc = OpenIDConnect(app)


@app.route('/')
def hello_world():
    if oidc.user_loggedin:
        return ('Hello, %s, <a href="/private">See private</a> '
                '<a href="/logout">Log out</a>') % \
            oidc.user_getfield('email')
    else:
        return 'Welcome anonymous, <a href="/private">Log in</a>'


@app.route('/private')
@oidc.require_login
def hello_me():
    return ('Hello, %s, <a href="/">Return</a>' % \
         oidc.user_getfield('name'))


@app.route('/api')
@oidc.accept_token(True, ['openid'])
def hello_api():
    return json.dumps({'hello': 'Welcome %s' % g.oidc_token_info['sub']})


@app.route('/logout')
def logout():
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
