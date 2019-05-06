from app import app

if __name__ == '__main__':
    # Why this session_type business?
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)