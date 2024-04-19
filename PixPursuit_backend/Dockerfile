# python 3.9 slim-buster as a parent image
FROM python:3.9-slim-buster

# Set specific versions for Google Chrome and ChromeDriver
ARG CHROME_VERSION="114.0.5735.133-1"
ARG CHROMEDRIVER_VERSION="114.0.5735.90"

# Install build dependencies for Annoy along with other required libraries and build tools
# Also, add the Google Chrome repository to the sources list
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    ca-certificates \
    software-properties-common \
    fonts-liberation \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    unzip \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxext6 \
    libxfixes3 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    gnupg \
    gcc \
    g++ \
    make \
    && echo "deb http://deb.debian.org/debian buster main contrib non-free" > /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list \
    && apt-get update

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install a specific version of Google Chrome
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

# Install a specific version of ChromeDriver
RUN wget -q --continue -P /tmp "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin \
    && rm /tmp/chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# Set the environment variable for Chrome
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container, this is the port that FastAPI will run on
EXPOSE 8000

# Set the environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
