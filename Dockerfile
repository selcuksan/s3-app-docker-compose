FROM python

# WORKDIR /s3-app

# COPY . .
# ENV S3_REGION = ""
# ENV ACCESS_KEY = ""
# ENV SECRET_KEY = ""
# ENV S3_ENDPOINT = ""
# S3 bucket adı
# ENV BUCKET_NAME = ''
# ENV UPLOAD_FOLDER = ''

COPY requirements.txt requirements.txt


RUN pip install -r requirements.txt


CMD ["python", "/s3-app/app/main.py"]

# docker exec -it 78740d05  bash