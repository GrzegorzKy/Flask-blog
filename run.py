# -*- coding: utf-8 -*-
from flaskblog import create_app


if __name__ == '__main__':
    app = create_app()
    app.run(port=9000, debug=True)
