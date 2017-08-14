from flask import session
from flask_dance import OAuth2ConsumerBlueprint
from flask_dance.consumer import oauth_authorized


def load_cern_oauth(app):
    """
       Loads the CERN Oauth into the application

       :param app: Flask application where the CERN Oauth will be loaded
       :return:
       """
    print(__name__)
    oauth = OAuth2ConsumerBlueprint(
        'cern_oauth',
        __name__,
        url_prefix='/oauth',
        # oauth specific settings
        token_url='https://oauth.web.cern.ch/OAuth/Token',
        authorization_url='https://oauth.web.cern.ch/OAuth/Authorize',
        # local urls
        login_url='/cern',
        authorized_url='/cern/authorized',
        client_id=app.config.get('CERN_OAUTH_CLIENT_ID', ''),
        client_secret=app.config.get('CERN_OAUTH_CLIENT_SECRET', '')
    )

    app.register_blueprint(oauth)

    @oauth_authorized.connect_via(oauth)
    def cern_logged_in(bp, token):
        # We don't keep the OAuth token since it's excessively long (~3kb) and we don't need
        # it anymore after getting the data here.
        response = oauth.session.get('https://oauthresource.web.cern.ch/api/User')

        response.raise_for_status()
        data = response.json()
        # flash("You are {first_name}".format(first_name=data['first_name'].strip()))

        session['user'] = {'username': data['username'].strip(),
                           'person_id': data['personid'],
                           'email': data['email'].strip(),
                           'first_name': data['first_name'].strip(),
                           'last_name': data['last_name'].strip()
                           }

        app.logger.info('OAuth login successful for %s (%s #%d)', data['username'], data['email'],
                        data['personid'])
