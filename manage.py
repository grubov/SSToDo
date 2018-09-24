from flask_script import Manager
from app.command import manager as command_manager
from app.app import app

manager = Manager(app)

manager.add_command("db", command_manager)

if __name__ == "__main__":
    manager.run()

