# 使用 AWS Lambda 的 Python 執行環境作為基本映像
FROM public.ecr.aws/lambda/python@sha256:c80401611e707039b37b5cd24b21f01bbcfa2583030123aee375cbcfa5becd5d

# 安裝所需的系統套件
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel

RUN curl -sS -o /tmp/google-chrome.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm && \
    yum localinstall -y /tmp/google-chrome.rpm && \
    rm /tmp/google-chrome.rpm

RUN pip install boto3==1.28.19
RUN pip install python-dotenv==1.0.0
RUN pip install beautifulsoup4==4.12.2
RUN pip install requests==2.31.0
RUN pip install html5lib==1.1
RUN pip install undetected-chromedriver==3.5.3


COPY main.py ./
COPY .env ./
CMD [ "main.handler" ]
