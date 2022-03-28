FROM python:3.9.12

WORKDIR /opt/fetcher
COPY *.py requirements.txt ./

RUN python3 -m pip install -r requirements.txt
 
CMD python3 forward.py --forever --wait-minutes 15