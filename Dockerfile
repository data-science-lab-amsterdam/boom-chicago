FROM dalloriam/python-dlib

WORKDIR /home/site/wwwroot

# install required packages
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy all files
COPY . .


EXPOSE 5000

# start flask app
ENTRYPOINT ["python"]
CMD ["src/flask-app.py"]
