FROM python:3.10-slim-bullseye

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get install -yq \
    ffmpeg

# install torch
RUN pip3 install \
        torch \
        torchvision \
        torchaudio \
        --extra-index-url https://download.pytorch.org/whl/cpu

# install other packages
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3"]
CMD ["app.py"]
