from waitress import serve

from sparrow.wsgi import application
import sys

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = sys.argv[1]

    serve(application, port=port)