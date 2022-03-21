FROM node as ui-build

WORKDIR /workspace

COPY ui/package.json ./
COPY ui/package-lock.json ./
RUN npm install --silent

COPY ui/ .

RUN npm run build


FROM golang:1.17 as go-builder

WORKDIR /workspace
# Copy the Go Modules manifests
COPY ./inspector/go.mod go.mod
COPY ./inspector/go.sum go.sum
# cache deps before building and copying source so that we don't need to re-download as much
# and so that source changes don't invalidate our downloaded layer
RUN go mod download

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