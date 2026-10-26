# Optional container (used by some directories to introspect tools). Data is NOT persisted unless you mount a volume.
FROM python:3.12-slim
LABEL io.modelcontextprotocol.server.name="io.github.jipbapkitchen/memory-lite"
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV MEMORY_LITE_DB=/data/memory.db
ENTRYPOINT ["memory-lite-mcp"]
