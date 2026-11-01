FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR=/run/oncall-config
ENTRYPOINT ["opsgenie-google-calendar-sync"]
CMD ["sync"]
