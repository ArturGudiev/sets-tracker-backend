#!/usr/bin/env python3
"""
Simple script to run the FastAPI server with database connectivity.
Make sure to install dependencies first: pip install -r requirements.txt
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
