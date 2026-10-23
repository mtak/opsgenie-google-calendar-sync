FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV ONCALL_SYNC_CONFIG_DIR=/run/oncall-config
ENTRYPOINT ["oncall-calendar-sync"]
CMD ["sync"]
