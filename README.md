## Runsync



### Development Setup
`sudo docker build -f Dockerfile-debug -t runsync-debug .`
`sudo docker rm -f runsync || true && sudo docker run --name runsync -p 8000:8000 -p 5678:5678 -v $(pwd):/app runsync-debug`
