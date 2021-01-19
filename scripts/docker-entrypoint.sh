#!/bin/sh

# Abort on any error (including if wait-for-it fails).
set -x

# Wait for the backend to be up, if we know where it is.
if [ -n "$RABBITMQ_HOST" ]; then
  ./wait-for-it.sh "$RABBITMQ_HOST:${RABBITMQ_PORT:-5672} --timeout 100"
fi

# Run the main container command.
exec "$@"
