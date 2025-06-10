# Use Home Assistant Python base image
ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:16.1.4
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Allow pip to modify system packages
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Setup base
RUN apk add --no-cache \
        python3 \
        python3-dev \
        py3-pip \
        openjdk11-jre-headless \
        chromium \
        chromium-chromedriver \
    && pip3 install --no-cache-dir \
        uk_bin_collection \
        selenium \
        requests \
        apscheduler \
        python-dateutil

# Set up Selenium
RUN wget -O /opt/selenium-server.jar "https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.33.0/selenium-server-4.33.0.jar"

# Copy root filesystem
COPY rootfs /

# Set working directory
WORKDIR /ukbincollectiondata

# Set up service scripts
COPY rootfs/etc/services.d/selenium /etc/services.d/selenium
COPY rootfs/etc/services.d/ukbincollectiondata /etc/services.d/ukbincollectiondata

# Set permissions
RUN chmod a+x /ukbincollectiondata/ukbincollectiondata.py \
    && chmod a+x /etc/services.d/selenium/run \
    && chmod a+x /etc/services.d/ukbincollectiondata/run

# Environment variables
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Labels
LABEL \
    io.hass.name="UK Bin Collection Data" \
    io.hass.description="UK Bin Collection Data integration for Home Assistant" \
    io.hass.type="addon" \
    io.hass.version="1.0.2" \
    maintainer="lsymds" \
    org.opencontainers.image.source="https://github.com/lsymds/hass-addons"
