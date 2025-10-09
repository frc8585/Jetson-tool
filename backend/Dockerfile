FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1

# Install system deps required by OpenCV and video utilities
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		git \
		ffmpeg \
		v4l-utils \
		libglib2.0-0 \
		libsm6 \
		libxrender1 \
		libxext6 \
	&& rm -rf /var/lib/apt/lists/*

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
