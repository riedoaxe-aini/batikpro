#!/bin/bash

echo "========================================="
echo "  Building BatikPro APK"
echo "========================================="

# Hapus Dockerfile yang salah
rm -f Dockerfile

# Buat Dockerfile yang benar
cat > Dockerfile << 'DOCKERFILE'
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/flutter/bin:${PATH}"

RUN apt-get update && apt-get install -y \
    curl git unzip zip wget \
    openjdk-17-jdk python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/flutter/flutter.git -b stable /root/flutter
RUN flutter doctor || true
RUN yes | flutter doctor --android-licenses || true

WORKDIR /app
COPY . .

RUN pip3 install flet pillow requests
RUN flet build apk

CMD ["ls", "-la", "build/apk/"]
DOCKERFILE

echo "✅ Dockerfile created"

# Build image
echo "Building Docker image..."
docker build -t batikpro-builder . 2>&1 | grep -E "Step|Successfully|ERROR"

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    echo "Trying alternative method..."
    
    # Alternative: Use python image
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget git unzip

RUN wget https://github.com/flutter/flutter/releases/download/3.16.0/flutter_linux_3.16.0-stable.tar.xz
RUN tar xf flutter_linux_3.16.0-stable.tar.xz -C /opt
ENV PATH="/opt/flutter/bin:${PATH}"

WORKDIR /app
COPY . .

RUN pip install flet pillow requests
RUN flet build apk
EOF
    
    docker build -t batikpro-builder . 
fi

echo "✅ Image built"

# Run
docker run --name batikpro-container batikpro-builder

# Copy APK
docker cp batikpro-container:/app/build/apk/BatikPro.apk . 2>/dev/null
docker rm batikpro-container

if [ -f "BatikPro.apk" ]; then
    echo "✅✅✅ SUCCESS! APK: BatikPro.apk"
    ls -lh BatikPro.apk
else
    echo "❌ Failed"
fi