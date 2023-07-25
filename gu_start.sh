#!/usr/bin/env bash
gunicorn -w 4 mm_server.mm:app
