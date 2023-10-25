FROM public.ecr.aws/lambda/python@sha256:c80401611e707039b37b5cd24b21f01bbcfa2583030123aee375cbcfa5becd5d

RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y

RUN pip install boto3==1.28.19
RUN pip install python-dotenv==1.0.0
RUN pip install mysql-connector-python==8.1.0



COPY main.py ./
COPY .env ./
CMD [ "main.handler" ]