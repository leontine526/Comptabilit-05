from flask.sessions import SecureCookieSessionInterface
from werkzeug.http import dump_cookie

class CompatibleSessionInterface(SecureCookieSessionInterface):
    """Interface de session compatible qui évite l'argument partitioned"""

    def save_session(self, app, session, response):
        if not session:
            if session.modified:
                response.delete_cookie(
                    app.config['SESSION_COOKIE_NAME'],
                    domain=self.get_cookie_domain(app),
                    path=self.get_cookie_path(app)
                )
            return

        # Si la session n'est pas modifiée, ne pas la sauvegarder
        if not self.should_set_cookie(app, session):
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.get_signing_serializer(app).dumps(dict(session))

        # Utiliser set_cookie sans l'argument partitioned
        response.set_cookie(
            app.config['SESSION_COOKIE_NAME'],
            val,
            expires=expires,
            httponly=httponly,
            domain=self.get_cookie_domain(app),
            path=self.get_cookie_path(app),
            secure=secure,
            samesite=self.get_cookie_samesite(app)
        )