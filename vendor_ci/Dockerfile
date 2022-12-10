FROM python:3.11.1-slim

WORKDIR /etc/vendor_ci

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY server.py .

# CMD [ "python3", "-m" , "flask", "--app", "server.py", "run", "--host=0.0.0.0"]
CMD [ "gunicorn", "server:app", "--bind", "0.0.0.0"]
