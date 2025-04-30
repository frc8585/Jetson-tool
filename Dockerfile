FROM stereolabs/zed:5.0-gl-devel-cuda12.6-ubuntu24.04

# 設定環境變數，防止互動式安裝程式卡住
ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES="all"
ENV NVIDIA_DRIVER_CAPABILITIES="all"

# 更新套件清單並安裝必要的依賴，包括編譯 Python 的相關套件
RUN apt update && apt install -y \
    usbutils \
    software-properties-common \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    cuda \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt upgrade -y

ENV PATH="$PATH:/usr/bin"

# 下載並編譯安裝 Python 3.12.8
WORKDIR /usr/src
RUN wget https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tgz \
    && tar -xf Python-3.12.8.tgz \
    && cd Python-3.12.8 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.8 Python-3.12.8.tgz

# 設定 python3 和 pip 預設指向 Python 3.12
RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3 \
    && ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3

# 確保 Python 安裝成功
RUN python3 --version && pip3 --version

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY . /app

RUN pip3 install --upgrade pip
RUN pip3 install requests
RUN python3 /usr/local/zed/get_python_api.py

# 安裝 Python 依賴
RUN pip3 install --no-cache-dir -r requirements.txt

# 設定 start.sh 為可執行
RUN chmod +x /app/start.sh

# 使用 entrypoint 執行腳本
CMD ["/app/start.sh"]
