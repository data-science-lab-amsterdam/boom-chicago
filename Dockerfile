FROM dalloriam/python-dlib

LABEL maintainer="robert.vanstraalen@datasciencelab.nl"

# web server root
WORKDIR /home/site/wwwroot

# install required packages
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy all files
COPY . .

# expose port 8000
EXPOSE 8000

# start flask app
CMD gunicorn -b :8000 src.app:app
