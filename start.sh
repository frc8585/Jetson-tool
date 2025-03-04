#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
uvicorn backend.main:app --reload