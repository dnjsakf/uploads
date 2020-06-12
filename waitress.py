from waitress import servei
from app import app

serve(app, unix_socket='unix.sock')