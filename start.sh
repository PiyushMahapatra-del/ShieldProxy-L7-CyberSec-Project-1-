#!/bin/bash
# Start the core website script in the background on port 8080
python core/website.py &

# Give it 2 seconds to bind to the port safely
sleep 2

# Start your front-facing proxy script in the foreground
python core/proxy.py