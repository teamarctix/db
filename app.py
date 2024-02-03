from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.String(255), nullable=False)
    api_hash = db.Column(db.String(255), nullable=False)
    bot_token = db.Column(db.String(255), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_id = request.form['api_id']
        api_hash = request.form['api_hash']
        bot_token = request.form['bot_token']

        user_input = UserInput(api_id=api_id, api_hash=api_hash, bot_token=bot_token)
        db.session.add(user_input)
        db.session.commit()

        # Redirect to avoid form resubmission on page refresh
        return redirect(url_for('index'))

    inputs = UserInput.query.all()
    return render_template('index.html', inputs=inputs)

@app.route('/delete_database', methods=['GET', 'POST'])
def delete_database():
    if request.method == 'GET':
        # Display a confirmation page before deleting
        return render_template('delete_confirm.html')

    elif request.method == 'POST':
        # Delete all entries in the UserInput table
        db.session.query(UserInput).delete()
        db.session.commit()

        return redirect(url_for('index'))
    
@app.route('/show_database')
def show_database():
    inputs = UserInput.query.all()
    return render_template('show_database.html', inputs=inputs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
