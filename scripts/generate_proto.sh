#!/bin/bash
python -m grpc_tools.protoc -I./proto --python_out=./server --grpc_python_out=./server ./proto/rf_settings.proto
cp ./server/rf_settings_pb2.py ./client/
cp ./server/rf_settings_pb2_grpc.py ./client/