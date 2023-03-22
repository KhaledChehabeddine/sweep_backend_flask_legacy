from app.factory import create_application

if __name__ == '__main__':
    application = create_application()
    application.config['DEBUG'] = True

    application.run(host='0.0.0.0')
