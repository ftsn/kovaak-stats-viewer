from kovaak_stats.app import create_app

application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=9999, debug=True)