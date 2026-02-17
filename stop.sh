#!/bin/bash

pkill -f "python receiver/receiver.py"
pkill -f "python processing/processing.py"
pkill -f "python storage/storage.py"
