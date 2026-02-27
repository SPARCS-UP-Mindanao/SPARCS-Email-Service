# Builder
FROM mcr.microsoft.com/devcontainers/base:debian AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev curl wget libncursesw5-dev xz-utils tk-dev \
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.8.20/Python-3.8.20.tar.xz \
    && tar -xf Python-3.8.20.tar.xz && cd Python-3.8.20 \
    && ./configure --enable-optimizations --prefix=/opt/python3.8 \
    && make -j$(nproc) && make install

ARG TARGETARCH
RUN case "${TARGETARCH:-amd64}" in amd64) ARCH="x86_64" ;; arm64) ARCH="aarch64" ;; *) exit 1 ;; esac \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip

# Slim Image
FROM mcr.microsoft.com/devcontainers/base:debian

ENV PATH="/opt/python3.8/bin:/usr/local/n/bin:${PATH}"
ENV N_PREFIX="/usr/local/n"
ENV PIPENV_VENV_IN_PROJECT=1

COPY --from=builder /opt/python3.8 /opt/python3.8
COPY --from=builder /tmp/aws /tmp/aws
RUN /tmp/aws/install && rm -rf /tmp/aws

# Install Node & Pipenv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://raw.githubusercontent.com/mklement0/n-install/stable/bin/n-install | bash -s -- -y 22 \
    && python3.8 -m pip install --no-cache-dir pipenv \
    && rm -rf /var/lib/apt/lists/*

# Install Dependencies (Pre-build)
WORKDIR /workspace
COPY package*.json ./
COPY Pipfile* ./

RUN npm install
RUN pipenv install --dev

# Verification
RUN python3.8 --version && node --version && aws --version
