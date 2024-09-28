FROM python:3.10.11-alpine3.17
ADD consumer.py .
COPY requirements.txt .
# Update Alpine Linux Package Manager and Install the bash
RUN apk update && apk add bash
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "consumer.py" ]