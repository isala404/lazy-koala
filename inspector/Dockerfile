FROM node as ui-build

WORKDIR /workspace

COPY ui/ .
RUN npm install --silent

RUN npm run build


FROM golang:1.17 as go-builder

WORKDIR /workspace

COPY ./inspector/ ./

# Copy UI build
COPY --from=ui-build /workspace/dist/ ui/

# Build
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o inspector main.go

# Use distroless as minimal base image to package the manager binary
# Refer to https://github.com/GoogleContainerTools/distroless for more details
FROM gcr.io/distroless/static:nonroot
COPY --from=go-builder /workspace/inspector /usr/local/bin/inspector
USER 65532:65532

ENTRYPOINT ["/inspector"]