# Store this code in 'app.py' file
# from https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' #put your password here
app.config['MYSQL_DB'] = 'shidduchdb'

mysql = MySQL(app)


@app.route('/')
def welcome():
    return render_template('welcome.html')
    # return "Welcome", '<a href = "login">click here to register.</a>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    # return render_template('register.html')
    msg = ''
    if request.method == 'POST' and 'user_name' in request.form and 'pwd' in request.form:
        print('in post and login')
        user_name = request.form['user_name']
        pwd = request.form['pwd']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM person WHERE user_name = % s AND pwd = % s', (user_name, pwd,))
        account = cursor.fetchone()
        print('before if account')
        if account:
            session['loggedin'] = True
            session['id'] = account['person_id']  # change this to the person id
            session['user_name'] = account['user_name']  # change this to the person full name
            msg = 'Logged in successfully !'
            print('supposed to render index now')
            return render_template('index.html', msg=msg)
        else:
            print('in the else')
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    print('in the register function')
    msg = ''
    if request.method == 'POST' and 'user_name' in request.form and 'pwd' in request.form \
            and 'gender' in request.form \
            and 'age' in request.form and "hebrew_name" in request.form and "height" in request.form and \
            'birthday' in request.form and 'full_name' in request.form:
        name = request.form['full_name']
        user_name = request.form['user_name']
        age = request.form['age']
        birthday = request.form['birthday']
        height = request.form['height']
        hebrew_name = request.form['hebrew_name']
        gender = request.form['gender']
        pwd = request.form['pwd']
        hashkafa = request.form['hashkafa']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print(cursor)
        cursor.execute('SELECT * FROM person WHERE user_name = % s', (user_name,))
        user = cursor.fetchone()

        if user:
            msg = "user already exists"

        if not hashkafa:
            msg = 'choose a hashkafa!'

        elif int(age) < 18:
            msg = "you do not meet the age requirement"

        else:
            cursor.execute('select hashkafa_id from hashkafa where hashkafa = %s', (hashkafa,))
            result = cursor.fetchone()
            for row in result:
                # print('row', result[row], 'end')
                hashkafa_gotten = result[row]

            print('hashkafa gotten', hashkafa_gotten)
            cursor.execute('INSERT INTO person (user_name, pwd, full_name, gender, age, hebrew_name, hashkafa_id, '
                           'birthday, height) '
                           'VALUES (% s, % s, %s, %s, % s, % s, %s, %s, %s)',
                           (user_name, pwd, name, gender, age, hebrew_name, hashkafa_gotten, birthday, height))

            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        print('in post method')
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    return redirect(url_for('login'))


@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select hashkafa_id from person where person_id = %s', (session['id'],))
        result = cursor.fetchone()

        for row in result:

            hashkafa_gotten = result[row]

        print('hashkafa gotten', hashkafa_gotten)
        cursor.execute('select * from hashkafa where hashkafa_id = %s', (hashkafa_gotten,))
        hashkafa = cursor.fetchone()
        cursor.execute('SELECT * FROM person WHERE person_id = % s', (session['id'],))
        account = cursor.fetchone()

        return render_template("display.html", account=account, hashkafa=hashkafa)
    return redirect(url_for('login'))


@app.route("/retrieve", methods=['POST', 'GET'])
def retrieve():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'hashkafa' in request.form and 'min_age' in request.form and 'max_age' in request.form:

            min_age = request.form['min_age']
            max_age = request.form['max_age']

            hashkafa = request.form['hashkafa']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('select hashkafa_id from hashkafa where hashkafa = %s', (hashkafa,))
            result = cursor.fetchone()
            for row in result:

                hashkafa_gotten = result[row]

            print('hashkafa gotten', hashkafa_gotten)
            cursor.execute(
                'select * from person where hashkafa_id = %s and age >= % s and age <= % s',
                (hashkafa_gotten, min_age, max_age)
            )
            rowcount = cursor.rowcount

            person_table = cursor.fetchall()
            msg = 'You have successfully searched !'
            print('did the search work?', 'after commit')
            if rowcount == 0:
                msg = 'No results'

            return render_template("retrieve_display.html", person_table=person_table, rowcount=rowcount, msg=msg)
        elif request.method == 'POST':
            msg = 'Please fill out the search bar !'

        return render_template("retrieve.html", msg=msg)

    return redirect(url_for('login'))


@app.route("/update", methods=['GET', 'POST'])
def update():
    # also update the display page
    msg = ''
    if 'loggedin' in session:
        print('loggin in update')
        if request.method == 'POST' and 'age' in request.form and 'birthday' in request.form \
                and 'gender' in request.form and 'height' in request.form and 'full_name' in request.form \
                and 'hebrew_name' in request.form and 'hashkafa' in request.form:
            print('in request post have pwd and username')
            hebrew_name = request.form['hebrew_name']
            gender = request.form['gender']
            age = request.form['age']
            full_name = request.form['full_name']
            height = request.form['height']
            birthday = request.form['birthday']
            hashkafa_name = request.form['hashkafa']
            print(hashkafa_name, 'hashkafa is')

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('select hashkafa_id from hashkafa where hashkafa = % s', (hashkafa_name,))
            # get that row of hashkafa id, should only be one row
            result = cursor.fetchone()
            for row in result:

                hashkafa_gotten = result[row]

            print('hashkafa gotten', hashkafa_gotten)
            cursor.execute(
                'UPDATE person set full_name = % s, gender = %s, age = %s, hebrew_name = % s, birthday = % s, '
                'height = % s, hashkafa_id = % s where person_id = % s',
                (full_name, gender, age, hebrew_name, birthday, height, hashkafa_gotten, (session['id'],),)
            )

            mysql.connection.commit()
            msg = 'You have successfully updated !'
            print('did the update work?', 'after commit')
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg=msg)

    return redirect(url_for('login'))


@app.route('/delete')
def delete():
    try:
        if 'loggedin' in session:
            print('in the delete')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM person WHERE person_id = % s', (session['id'],))
            print('after cursor user id')
            account = cursor.fetchone()
            print('go an account')
            if account:
                print('in the delete')
                cursor.execute("DELETE FROM person WHERE person_id=%s", (session['id'],))
                mysql.connection.commit()
                flash('User deleted successfully!')
                return redirect('/')
        return render_template("delete.html", account=account)
    except Exception as e:
        print('failed delete')
        print(e)
    return redirect(url_for('login'))

    return render_template('login.html')


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
