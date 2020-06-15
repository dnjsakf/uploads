from app import app
from waitress import serve
from paste.translogger import TransLogger

if __name__ == '__main__':
  serve(TransLogger(app, setup_console_handler=False), host="0.0.0.0", port="3000")