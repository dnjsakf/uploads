import os
import pprint
import dotenv
import psutil
import werkzeug
import tempfile

from flask import (
  Flask, request, redirect, url_for
  , Response, stream_with_context
  , send_from_directory
)

APP_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_BASE = os.path.join(APP_PATH, 'static/files')

def check_save_path(save_path):
  if not os.path.isdir( save_path ):
    os.makedirs( save_path )
  return save_path


app = Flask(__name__, 
  static_url_path="/static/",
  static_folder="./static"
)
app.config["FILE_BASE"] = FILE_BASE

@app.route("/", methods=["GET","POST"])
def index():
  save_path = check_save_path(app.config["FILE_BASE"])
  files = os.listdir(save_path)
  
  app.logger.info(files)
  
  html = [
  '''
  <form id="multiple_upload" method="POST" action="/static/upload" enctype="multipart/form-data">
    <input type="file" name="multiple_file" multiple="multiple">
    <button>static upload</button>
  </form>
  ''',
  '''
    <form id="multiple_upload" method="POST" action="/stream/upload" enctype="multipart/form-data">
    <input type="file" name="multiple_file" multiple="multiple">
    <button>streaming upload</button>
  </form>
  '''
  ]
  
  html.append('<ul>')
  for f in files:
    #html.append( '<li><a href="/download/{}">{}</a></li>'.format( f, f ) )
    html.append( '<li><a href="http://localhost:4000/static/files/{}">{}</a></li>'.format( f, f ) )
  html.append('</ul>')

  return "\n".join( html )
  
@app.route('/download', methods=['GET', 'POST'])
@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename=None):
  save_path = check_save_path(app.config["FILE_BASE"])
  
  if filename is not None:
    return send_from_directory(directory=save_path, filename=filename)
  else:
    return send_from_directory(directory=save_path)

  
@app.route("/static/upload", methods=["POST"])
def do_statc_upload():
  save_path = check_save_path(app.config["FILE_BASE"])
  app.logger.info('save to ===> '+str(save_path))
    
  app.logger.info('start receive request')
  upload_files = request.files.getlist("multiple_file")
  app.logger.info('end receive request')
  
  for f in upload_files:
    app.logger.info("start save => " + f.filename)
    f.save(os.path.join(save_path, werkzeug.utils.secure_filename(f.filename)))
    app.logger.info("end save => " + f.filename)
    
  process = psutil.Process(os.getpid())
  
  app.logger.info("memory usage: %.1f MiB" % (process.memory_info().rss / (1024.0*1024.0)))
  
  return redirect(url_for('index'))

  
@app.route('/stream/upload', methods = ['POST'])
def do_stream_upload():
  save_path = check_save_path(app.config["FILE_BASE"])
  app.logger.info('save to ===> '+str(save_path))
  
  app.logger.info('start receive request')
  def custom_stream_factory(total_content_length, filename, content_type, content_length=None):
    app.logger.info("start save => " + filename)    
    return open(os.path.join(save_path, filename), 'wb+')
  app.logger.info('end receive request')
  
  stream, form, files = werkzeug.formparser.parse_form_data(request.environ, stream_factory=custom_stream_factory)
  stream_size = 0
  
  # Generate
  app.logger.info('start streaming')
  for f in files.values():
    app.logger.info(" ".join(["end save args=", f.name, "submitted as", f.filename, "to ", f.stream.name]))
    stream_size += os.path.getsize( f.stream.name )
  app.logger.info('end streaming')
  
  process = psutil.Process(os.getpid())
  
  app.logger.info("memory usage: %.1f MiB" % (process.memory_info().rss / (1024.0*1024.0)))
  app.logger.info("total size: %.1f MiB" % (stream_size / (1024.0*1024.0)))

  return redirect(url_for('index'))
  
if __name__ == '__main__':
  dotenv.load_dotenv(dotenv_path=".env")
  
  app.run(host="0.0.0.0", port="3000")