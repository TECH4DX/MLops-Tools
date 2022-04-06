FROM alpine/git:v2.32.0
RUN git clone https://github.com/guoqiangqi/mnist-serving.git /mnist-serving

FROM python:3.5-slim
COPY --from=0 /mnist-serving /mnist-serving
WORKDIR /mnist-serving
RUN pip3 install -r requirements.txt
#CMD ["python main.py"]
