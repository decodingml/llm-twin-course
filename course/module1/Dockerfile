FROM  public.ecr.aws/lambda/python:3.11 as build

# Install chrome driver and browser
RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1135561%2Fchrome-linux.zip?alt=media" && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/chrome-linux.zip -d /opt/

FROM  public.ecr.aws/lambda/python:3.11

# Install the function's OS dependencies using yum
RUN yum install -y \
    atk \
    wget \
    git \
    cups-libs \
    gtk3 \
    libXcomposite \
    alsa-lib \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    at-spi2-atk \
    libXt \
    xorg-x11-server-Xvfb \
    xorg-x11-xauth \
    dbus-glib \
    dbus-glib-devel \
    nss \
    mesa-libgbm \
    ffmpeg \
    libxext6 \
    libssl-dev \
    libcurl4-openssl-dev \
    libpq-dev


COPY --from=build /opt/chrome-linux /opt/chrome
COPY --from=build /opt/chromedriver /opt/

COPY poetry.lock pyproject.toml ./

# Install Poetry, export dependencies to requirements.txt, and install dependencies
# in the Lambda task directory, finally cleanup manifest files.
RUN python3 -m pip install --upgrade pip && pip3 install poetry
RUN poetry export -f requirements.txt > requirements.txt && \
    pip3 install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}" && \
    rm requirements.txt pyproject.toml poetry.lock

# Optional TLS CA only if you plan to store the extracted data into Document DB
RUN wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -P ${LAMBDA_TASK_ROOT}

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["main.handler"]
