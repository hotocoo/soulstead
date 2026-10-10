# SOULSTEAD relay server.
# Build:  docker build -t soulstead-relay server/
# Run:    docker run -e PORT=8080 -p 8080:8080 soulstead-relay
FROM debian:bookworm-slim

ARG GODOT_VERSION=4.7.2
ENV PORT=8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/godot.zip \
      "https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}-stable/Godot_v${GODOT_VERSION}-stable_linux.x86_64.zip" \
    && unzip /tmp/godot.zip -d /usr/local/bin \
    && mv /usr/local/bin/Godot_v${GODOT_VERSION}-stable_linux.x86_64 /usr/local/bin/godot \
    && chmod +x /usr/local/bin/godot \
    && rm /tmp/godot.zip

WORKDIR /srv/relay
COPY . /srv/relay

EXPOSE 8080
CMD ["godot", "--headless", "--path", "/srv/relay"]
