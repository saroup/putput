ARG PYTHON_VERSION=3.7

FROM python:${PYTHON_VERSION} AS build
COPY requirements*.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt \
 && pip install --no-cache-dir -r /app/requirements-dev.txt
COPY . /app
WORKDIR /app
RUN ["python", "setup.py", "mypy", "pylint", "test", "sdist", "bdist_wheel"]

FROM python:${PYTHON_VERSION}-slim AS samples
COPY --from=build /app/samples /samples
COPY --from=build /app/dist /dist
RUN pip install --no-cache-dir /dist/*
WORKDIR /samples
ENTRYPOINT ["python", "-m"]
CMD ["smart_speaker"]
