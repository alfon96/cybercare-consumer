FROM python:3.12-slim

# Create the vscode user
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 -m vscode

WORKDIR /app

# install libs
RUN apt-get update --allow-releaseinfo-change \
    && apt-get install -y --no-install-recommends git make build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# install poetry (as root)
RUN pip install --no-cache poetry==1.8.4

# give /app to vscode and switch user
RUN chown -R vscode:vscode /app
USER vscode

# copy only the manifest
COPY --chown=vscode:vscode pyproject.toml ./

# create venv in vscode's home (NOT inside /app, so volumes won't hide it)
RUN poetry install --no-root --no-cache

# copy source
COPY --chown=vscode:vscode src ./src

# always run through poetry env
CMD ["poetry", "run", "python", "-u", "-m", "src.main"]
