from views import app

if __name__ == "__main__":
    app.debug = True
    app.run(
        use_reloader = False,
        host = 'localhost',
        port=5003
    )