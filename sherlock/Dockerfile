# Build the binary
FROM ekidd/rust-musl-builder as builder
WORKDIR /sherlock
USER root

# Copy the source and build the application.
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --target x86_64-unknown-linux-musl --release


# Production Image
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /app
# COPY the binary
RUN mkdir -p /app/models
COPY --from=builder /sherlock/target/x86_64-unknown-linux-musl/release/sherlock /app/sherlock

# DEFAULT ENV
ENV END_POINT=http://localhost:8501/v1/models
ENV POOL_DURATION=60
# Define port
EXPOSE 9898

CMD ["/app/sherlock"]