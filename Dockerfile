FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir -p /app

WORKDIR /app

ENV PYTHONPATH=/app

RUN curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/download/v1.7.0/dbmate-linux-amd64
RUN chmod +x /usr/local/bin/dbmate

ADD ./requirements.txt ./requirements.txt

RUN mkdir /tmp/.pip && \
	pip install --cache-dir=/tmp/.pip --upgrade pip && \
	pip install --cache-dir=/tmp/.pip -r ./requirements.txt && \
	rm -fr /tmp/.pip

ADD ./ ./

EXPOSE 8000

CMD ["/bin/bash", "deploy/run-container.sh"]
