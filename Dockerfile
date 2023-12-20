FROM python:3.8-alpine
LABEL maintainer="Leonid"
COPY ./techtrends/requirements.txt ./
COPY ./techtrends ./
RUN python init_db.py
RUN pip install -r requirements.txt
EXPOSE 3111
CMD [ "python", "app.py" ]
