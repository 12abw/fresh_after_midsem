@app.route('/selectedImages', methods=['POST', 'GET'])
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
    current_directory = os.path.dirname(_file_)
    static_folder_path = os.path.join(current_directory, 'templates')
    temp_img_folder_path = os.path.join(static_folder_path, 'images')
    os.makedirs(temp_img_folder_path, exist_ok=True)

    # Save the image data to temporary files and store their filenames in the list
    image_files = []

    for image_data in images_data:
        imageid = image_data['imageid']
        file_name = f'selected_{imageid}.jpg'
        file_path = os.path.join(temp_img_folder_path, file_name)  # Use os.path.join to create the full path
        with open(file_path, 'wb') as file:
            file.write(image_data['image'])
        image_files.append(file_name)

    conn.close()

    # Render user profile template with user's details
    if user:
        return render_template('video.html', user=user, image_file=image_files)
    else:
        return "User not found."


# Route to serve the images from the temporary folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
   return send_file(os.path.join(app.root_path, 'static', filename))

# Route to serve the images from the temporary folder
@app.route('/selected_uploads/<filename>')
def selected_uploads(filename):
   return send_file(os.path.join(app.root_path, 'templates', filename))