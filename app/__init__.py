from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    with app.app_context():
        from . import routes

        # Configuração da chave secreta para JWT
        app.config['SECRET_KEY'] = 'sua_chave_secreta'

        app.register_blueprint(routes.main)

        return app
