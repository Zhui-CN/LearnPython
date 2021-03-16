from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from flask_wtf.csrf import generate_csrf

app = create_app('development')
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.after_request
def after_request(response):
    csrf_token = generate_csrf()
    response.set_cookie("csrf_token", csrf_token)
    return response


if __name__ == '__main__':
    manager.run()
