import os
import io
import errno
import zipfile
from werkzeug.utils import secure_filename
from flask import Flask, flash, request

from config import settings


def unzip(zip_file, extraction_path):
    """
    code to unzip files
    """
    print "[INFO] Unzipping"
    try:
        files = []
        with zipfile.ZipFile(zip_file, "r") as z:
            for fileinfo in z.infolist():
                filename = fileinfo.filename
                dat = z.open(filename, "r")
                files.append(filename)
                outfile = os.path.join(extraction_path, filename)
                if not os.path.exists(os.path.dirname(outfile)):
                    try:
                        os.makedirs(os.path.dirname(outfile))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            print "\n[WARN] OS Error: Race Condition"
                if not outfile.endswith("/"):
                    with io.open(outfile, mode='wb') as f:
                        f.write(dat.read())
                dat.close()
        return files
    except Exception as e:
        print "[ERROR] Unzipping Error" + str(e)


def html_escape(text):
    """Produce entities within text."""
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def allowed_file(filename):
    """Allowed File"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTS

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    """Handle Upload"""

    if request.method == 'POST':
        extraction_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "uploads")
        if 'file' not in request.files:
            flash('No file part')
            return "No File part!"
        file_uploaded = request.files['file']
        if file_uploaded.filename == '':
            flash('No selected file')
            return "No File Selected!"
        if file and allowed_file(file_uploaded.filename):
            filename = secure_filename(file_uploaded.filename)
            write_to_file = os.path.join(extraction_path, filename)
            file_uploaded.save(write_to_file)
            unzip(write_to_file, extraction_path)
            return "<b>Uploaded to</b> " + html_escape(write_to_file) + "<br>" + "<b>Content Extracted to</b> " + html_escape(extraction_path)


@app.route('/', methods=['GET'])
def main():
    """Home"""
    html = '''
    <form enctype="multipart/form-data" action="/upload" method="POST">
    Choose a file to upload:
    <input name="file" type="file" accept=".zip,.apk" />
    <input type="submit" value="Upload" />
    </form>
    '''
    return html

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(threaded=True, host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
