FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r putput/requirements.txt && chmod +x ci.sh
CMD ./ci.sh