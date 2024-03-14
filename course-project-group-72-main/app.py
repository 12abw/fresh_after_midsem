from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt
import jwt
import datetime
from werkzeug.utils import secure_filename
from mysql.connector import Binary
import os  # Import the os module

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'my secret key'

# Additional configuration for file upload to a separate database
db_config = {
   'host': 'localhost',
   'user': 'root',
   'password': 'newp',
   'database': 'amigos_project'
}

def connect_to_mysql():
   try:
      conn = mysql.connector.connect(**db_config)
      if conn.is_connected():
         print(f'Connected to MySQL database')
         return conn
   except Error as e:
      print(e)


def close_connection(conn):
   if conn.is_connected():
      conn.close()
      print('Connection to MySQL database closed')



# def create_users_table():
#     with conn.cursor() as cursor:
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS users_details (
#                 userid INT AUTO_INCREMENT PRIMARY KEY,
#                 username VARCHAR(255) COLLATE utf8mb4_bin NOT NULL UNIQUE,
#                 email VARCHAR(255) UNIQUE,
#                 fullname VARCHAR(255) NOT NULL,
#                 password VARCHAR(255) NOT NULL UNIQUE
#             )
#         """)
#         connection.commit()

# def create_images_table():
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS images_table  (
#                imageid INT PRIMARYKEY AUTO_INCREMENT,
#                userid INT NOT ,
#               image LONGBLOB ,        
#             )
#         """)
#         connection.commit()
def create_users_table():
    conn = connect_to_mysql()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users_details (
                        userid INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) COLLATE utf8mb4_bin NOT NULL UNIQUE,
                        email VARCHAR(255) UNIQUE,
                        fullname VARCHAR(255) NOT NULL,
                        password VARCHAR(255) NOT NULL
                    )
                """)
                conn.commit()
        finally:
            close_connection(conn)

# Create images table
def create_images_table():
    conn = connect_to_mysql()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS images_table (
                        imageid INT AUTO_INCREMENT PRIMARY KEY,
                        userid INT NOT NULL,
                        image LONGBLOB
                    )
                """)
                conn.commit()
        finally:
            close_connection(conn)


def create_audio_files():
    conn = connect_to_mysql()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audio_files (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        audio_name VARCHAR(255) ,
                        audio_data LONGBLOB
                    )
                """)
                conn.commit()
        finally:
            close_connection(conn)


def generate_token(username):
    expiry_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {'username': username, 'exp': expiry_date}
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')
    return token   

# Function to verify JWT token
def verify_token(token):
    try:
        payload = jwt.decode(token,app.secret_key, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None     


@app.route('/')
def index():
   return render_template('index.html')




# def save_files_to_database(userid, file_names):
#    try:
#       conn = connect_to_mysql()
#     #   conn = mysql.connector.connect(**db_config)
#       print("Connected to MySQL")
#       cursor = conn.cursor()

#       for file_name in file_names:
#          with open(file_name, 'rb') as file:
#                image_data = file.read()
#                # Insert each image separately
#                cursor.execute('''
#                   INSERT INTO images_table (userid, image)
#                   VALUES (%s, %s)
#                ''', (userid, Binary(image_data)))
#                conn.commit()


#       flash('Files saved to the database successfully', 'success')

#    except Error as e:
#       flash(f'Error saving files to the database: {str(e)}', 'error')

#    finally:
#       cursor.close()
#       close_connection(conn)


def save_files_to_database(userid, file_names):
    try:
        conn = mysql.connector.connect(**db_config)
        print("Connected to MySQL")
        cursor = conn.cursor()

        for file_name in file_names:
            with open(file_name, 'rb') as file:
                image_data = file.read()
                # Insert each image separately
                cursor.execute('''
                    INSERT INTO images_table (userid, image)
                    VALUES (%s, %s)
                ''', (userid, mysql.connector.Binary(image_data)))
                conn.commit()

        print('Files saved to the database successfully')

    except Error as e:
        print(f'Error saving files to the database: {str(e)}')

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

def save_selected_files_to_database(userid, file_names):
    try:
        conn = mysql.connector.connect(**db_config)
        print("Connected to MySQL")
        cursor = conn.cursor()

        for file_name in file_names:
            with open(file_name, 'rb') as file:
                image_data = file.read()
                # Insert each image separately
                cursor.execute('''
                    INSERT INTO images_table (userid, selected_images)
                    VALUES (%s, %s)
                ''', (userid, mysql.connector.Binary(image_data)))
                conn.commit()

        print('Files saved to the database successfully')

    except Error as e:
        print(f'Error saving files to the database: {str(e)}')

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()



@app.route('/signup', methods=['POST','GET'])
def signup():
    error = None
    # error_mssg = None
    conn = connect_to_mysql()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fullname = request.form['fullname']
        password = request.form['password']
        

        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
        # import re
        # if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return render_template('index.html', error="Invalid email format. Please enter a valid email.")

        # Here you can process the data (e.g., save to database) 
        # and redirect to a success page
        # For demonstration, let's just print the data
        # print(f"Username: {username}, Email: {email}, Fullname: {fullname}, Password: {password}")


        # Check if the username or email already exists
        cursor.execute("SELECT * FROM users_details WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            error = "User with this username or email already exists."
            return render_template('index.html', error=error)  # Render the signup page with the error message
        else:
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the new user into the database
            insert_query = "INSERT INTO users_details (username, email, fullname, password) VALUES (%s, %s, %s, %s)"
            user_data = (username, email, fullname, hashed_password)
            cursor.execute(insert_query, user_data)
            conn.commit()

             # Fetch the newly created user to get the userid
            cursor.execute("SELECT userid FROM users_details WHERE username = %s", (username,))
            new_user = cursor.fetchone()
            if new_user:
                session['userid'] = new_user['userid']  # Set userid in session
                flash('User registered successfully. Please log in.', 'success')
                close_connection(conn)
                return redirect(url_for('mult_image'))  # Redirect to the index page

            # close_connection(conn)
            # return redirect(url_for('mult_image'))  # Redirect to the success route

    return render_template('index.html', error=error)





        
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        conn = connect_to_mysql()
        cursor = conn.cursor(dictionary=True)

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        cursor.execute("SELECT * FROM users_details WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):
            token = generate_token(username)
            session['userid'] = user['userid']
            conn.close()
            return redirect(url_for('user_profile', username=username, token=token))
        else:
            error_msg = 'Invalid username or password'
            session['error_msg'] = error_msg
            conn.close()
            return redirect(url_for('login'))
    else:
        # If error message is in session, retrieve and then delete it
        error_msg = session.pop('error_msg', None)
        return render_template('index.html', error_msg=error_msg)


def connectt_to_mysql():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='newp',
        database='amigos_project'
    )
@app.route('/user_profile/<username>', methods=['POST', 'GET'])
def user_profile(username):
    token = request.args.get('token')
    verified_username = verify_token(token)
    
    if verified_username == username:
        conn = connect_to_mysql()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users_details WHERE username = %s", (verified_username,))
        user = cursor.fetchone()
        
        # if user:
        # Retrieve all images for the logged-in user
        userid = user['userid']
        session['userid'] = user['userid']
        session['username'] = user['username']
        cursor.execute("SELECT imageid, image FROM images_table WHERE userid = %s", (userid,))
        images_data = cursor.fetchall()

        current_directory = os.path.dirname(__file__)
        static_folder_path = os.path.join(current_directory, 'static')
        temp_img_folder_path = os.path.join(static_folder_path, 'images')
        os.makedirs(temp_img_folder_path, exist_ok=True)
   # Save the image data to temporary files and store their filenames in the list

   # Create a list to store the image file names
        image_files = []

        for image_data in images_data:
            imageid = image_data['imageid']
            file_name = f'temp_{imageid}.jpg'
            file_path = os.path.join(temp_img_folder_path, file_name)  # Use os.path.join to create the full path
            with open(file_path, 'wb') as file:
                file.write(image_data['image'])
            image_files.append(file_name)

        conn.close()

   # Render user profile template with user's details
#    return render_template('user_page.html', user=user, image_files=image_files)
        
        if user:
            conn.close()
            return render_template('user_page.html', user=user,image_files=image_files)
        else:
            return "User not found."
    else:
        return "Unauthorized access."


@app.route('/selectedImages')
def selectedImages():
    username = session.get('username')

    if not username:
        return "User not logged in."

    conn = connect_to_mysql()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users_details WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found."

    # Retrieve all images for the logged-in user
    userid = user['userid']
    cursor.execute("SELECT imageid, image FROM images_table WHERE userid = %s", (userid,))
    images_data = cursor.fetchall()

    current_directory = os.path.dirname(__file__)
    static_folder_path = os.path.join(current_directory, 'templates')
    temp_img_folder_path = os.path.join(static_folder_path, 'images')
    os.makedirs(temp_img_folder_path, exist_ok=True)

    # Save the image data to temporary files and store their filenames in the list
    selected_image_files = []

    for image_data in images_data:
        imageid = image_data['imageid']
        file_name = f'selected_{imageid}.jpg'
        file_path = os.path.join(temp_img_folder_path, file_name)  # Use os.path.join to create the full path
        with open(file_path, 'wb') as file:
            file.write(image_data['image'])
        selected_image_files.append(file_name)

    conn.close()

    # Render user profile template with user's details
    if user:
        return render_template('video.html', user=user, image_file=selected_image_files)
    else:
        return "User not found."


# Route to serve the images from the temporary folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
   return send_file(os.path.join(app.root_path, 'static', filename))

# Route to serve the images from the temporary folder
@app.route('/selected_uploads/<filename>')
def selected_uploads(filename):
   return send_file(os.path.join(app.root_path, 'templates','images', filename))


@app.route('/upload_files', methods=['POST'])
def upload_files():
 # Retrieve userid from the session
   userid = session.get('userid')
   if not userid:
      flash('User not logged in', 'error')
      return redirect(url_for('login'))  
    
   image_files = request.files.getlist('image')

   if image_files:
      file_names = []

      for image_file in image_files:
         file_name = secure_filename(image_file.filename)
         image_file.save(file_name)
         file_names.append(file_name)

      save_files_to_database(userid, file_names)

      flash('Files uploaded and saved to the database successfully', 'success')

   return 'Files uploaded successfully'


@app.route('/upload_seleted_files', methods=['POST'])
def upload_seleted_files():
 # Retrieve userid from the session
   userid = session.get('userid')
   if not userid:
      flash('User not logged in', 'error')
      return redirect(url_for('login'))  
    
   image_files = request.files.getlist('image')

   if image_files:
      file_names = []

      for image_file in image_files:
         file_name = secure_filename(image_file.filename)
         image_file.save(file_name)
         file_names.append(file_name)

      save_files_to_database(userid, file_names)

      flash('Files uploaded and saved to the database successfully', 'success')

   return 'Files uploaded successfully'


@app.route('/get_selected_images', methods=['GET'])
def get_selected_images():
 # Retrieve userid from the session
   userid = session.get('userid')
   if not userid:
      flash('User not logged in', 'error')
      return redirect(url_for('login'))  
    
   selected_image_files = request.files.getlist('image')

   if selected_image_files:
      file_names = []

      for image_file in selected_image_files:
         file_name = secure_filename(image_file.filename)
         image_file.save(file_name)
         file_names.append(file_name)

      save_files_to_database(userid, file_names)

      flash('Files uploaded and saved to the database successfully', 'success')

   return 'Files uploaded successfully'



def insert_audio_files(file_paths):
    try:
        # Database connection configuration
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'newp',
            'database': 'amigos_project'
        }

        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        for file_path in file_paths:
            # Read audio file as binary data
            with open(file_path, 'rb') as audio_file:
                audio_data = audio_file.read()

            # Insert audio data into the database
            insert_query = "INSERT INTO audio_files (audio_data) VALUES (%s)"
            cursor.execute(insert_query, (audio_data,))

        # Commit the changes
        connection.commit()

        print("Audio files inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

# Example: Insert five audio files into the database
audio_file_paths = [
   'audio1.mp3',
   'audio2.mp3',
   'audio3.mp3',
   'audio4.mp3',
   'audio5.mp3',
]

# insert_audio_files(audio_file_paths)


@app.route('/multImage')
def mult_image():
    return render_template('multImag.html')



@app.route('/video')
def video():
    return render_template('video.html')


insert_audio_files(audio_file_paths)

# Add this route to serve audio options
@app.route('/get_audio_options')
def get_audio_options():
    try:
        conn = connect_to_mysql()
        cursor = conn.cursor(dictionary=True)

        # Fetch audio options from the database
        cursor.execute("SELECT filename, filepath FROM audio_files")
        audio_options = cursor.fetchall()

        # Close the database connection
        cursor.close()
        close_connection(conn)

        return jsonify(audio_options)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    create_users_table()  # Create the users table if it doesn't exist
    create_images_table()
    create_audio_files()
    
    app.run(debug=True, port=5007)