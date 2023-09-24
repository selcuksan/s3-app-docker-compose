import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# AWS S3 erişim anahtarları
S3_REGION = os.environ["S3_REGION"]
ACCESS_KEY = os.environ["ACCESS_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]
S3_ENDPOINT = os.environ["S3_ENDPOINT"]
# http://127.0.0.1:9000
BUCKET_NAME = os.environ["BUCKET_NAME"]
UPLOAD_FOLDER = "/s3-app/downloads/" #os.environ["UPLOAD_FOLDER"]

# Flask uygulamasının ayarları
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# minio session
def create_session(ACCESS_KEY, SECRET_KEY, S3_ENDPOINT):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY, endpoint_url=S3_ENDPOINT)
    return s3


# AWS S3'ye dosya yükleme
def upload_to_s3(local_file, s3_file):
    s3 = create_session(ACCESS_KEY, SECRET_KEY, S3_ENDPOINT)
    try:
        s3.upload_file(local_file, BUCKET_NAME, s3_file)
        return True
    except FileNotFoundError:
        return False
    except NoCredentialsError:
        return False


@app.route('/', methods=['GET'])
def home():
    return render_template("files.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        for file in request.files.getlist('file'):
            print(file)
            filename = file.filename
            # content_type = file.content_type
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
                filename = os.path.join(
                    app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                if upload_to_s3(filename, file.filename):
                    os.remove(filename)
                # return redirect('/'), "Files uploaded successfully"
                    return redirect(url_for('list_files'))

    return 'File could not be uploaded'


# Dosya listeleme ve silme
@app.route('/files')
def list_files():
    s3 = create_session(ACCESS_KEY, SECRET_KEY, S3_ENDPOINT)
    objects = objects = s3.list_objects(Bucket=BUCKET_NAME)['Contents']
    # return objects
    return render_template('files.html', files=objects)


@app.route('/download/<filename>')
def download_file(filename):
    s3 = create_session(ACCESS_KEY, SECRET_KEY, S3_ENDPOINT)
    try:
        local_file_path = os.path.join(UPLOAD_FOLDER, filename)
        s3.download_file(BUCKET_NAME, filename, local_file_path)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as err:
        return f"Dosya İndirme Hatası: {str(err)}"

@app.route('/delete/<filename>')
def delete_file(filename):
    s3 = create_session(ACCESS_KEY, SECRET_KEY, S3_ENDPOINT)
    response = s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    print(response)
    if response['ResponseMetadata']['HTTPStatusCode'] == 204:
        return redirect(url_for('list_files'))
        # return f"{filename} başarıyla silindi."
    else:
        return f"Silme işlemi başarısız. HTTPStatusCode: {response['ResponseMetadata']['HTTPStatusCode']}"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
