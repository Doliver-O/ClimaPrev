from app import create_app
from flask_login import LoginManager
from models import User
from flask import Blueprint, render_template, jsonify,request,send_file, Flask
from flask import Flask, render_template
from waitress import serve



app = create_app()


app.config['SECRET_KEY'] = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.errorhandler(401)
def unauthorized(error):
    return render_template('unauthorized.html', title='Unauthorized')


if __name__ == "__main__":
    #serve(app, host='0.0.0.0', port=8080)
    app.run(debug=True)
