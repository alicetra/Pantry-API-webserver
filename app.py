from setup import app
from jwt_config import jwt
from blueprints.cli_bp import db_commands
from blueprints.users_bp import users_bp

app.register_blueprint(db_commands)
app.register_blueprint(users_bp)
jwt.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
