ARG PYTHON_VERSION=3.7

FROM python:${PYTHON_VERSION} AS build
COPY requirements*.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt \
 && pip install --no-cache-dir -r /app/requirements-dev.txt \
 && pip install --no-cache-dir -r /app/requirements-dev-ml.txt
COPY . /app
WORKDIR /app
RUN python setup.py mypy pylint \
 && coverage run setup.py test \
 && python setup.py sdist bdist_wheel \
 && pip install --no-cache-dir dist/* \
 && jupyter nbconvert samples/**/*.ipynb --to python \
 && export CI=True \
 && set -e \
 && for sample in samples/**/*.py; do python $sample; done

FROM python:${PYTHON_VERSION}-slim AS samples
COPY --from=build /app/samples /samples
COPY --from=build /app/dist /dist
COPY --from=build /app/.coverage /.coverage
RUN pip install --no-cache-dir /dist/*
WORKDIR /samples
ENTRYPOINT ["python", "-m"]
CMD ["smart_speaker"]
