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

# COPY the binary
COPY --from=builder /sherlock/target/x86_64-unknown-linux-musl/release/sherlock /sherlock

# DEFAULT ENV
ENV SERVICE_NAME=sample_service
ENV NAMESPACE=default
ENV END_POINT=http://localhost:8501/v1/models/sherlock:predict
ENV POOL_DURATION=60

# Define port
EXPOSE 9898

CMD ["/sherlock"]