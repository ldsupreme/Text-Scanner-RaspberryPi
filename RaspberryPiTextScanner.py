import cv2
import pytesseract
import smtplib
import picamera
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Initialize Tkinter
root = tk.Tk()
root.title("Tesseract OCR GUI")

# Global variables
captured_image = ""
extracted_text = ""
photo_display = None  # Global reference to the displayed image

# Function to capture image
def capture_image():
    global captured_image, photo_display
    currentTime = datetime.now()
    captured_image = "/home/pi/picam/" + currentTime.strftime("%Y.%m.%d-%H%M%S") + '.jpg'
    
    with picamera.PiCamera() as camera:
        camera.resolution = (600, 300)
        camera.capture(captured_image)
        # Load the captured image for display
        image = Image.open(captured_image)
        photo_display = ImageTk.PhotoImage(image)
        image_display.config(image=photo_display)
    messagebox.showinfo("Success", "Image Captured!")


# Function to perform OCR and send email
def perform_ocr_send_email():
    global extracted_text
    img = cv2.imread(captured_image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    extracted_text = pytesseract.image_to_string(img_gray, config='')

    currentTime = datetime.now()
    txt_name = "/home/pi/picam/" + currentTime.strftime("%Y.%m.%d-%H%M%S") + '.txt'
    with open(txt_name, "w") as f:
        f.write(extracted_text)
    text_box.delete(1.0, tk.END)  # Clear previous content
    text_box.insert(tk.END, extracted_text)  # Update the text box
    send_email(txt_name)


# Function to send email
def send_email(txt_file):
    email_sender = 'ldbraspberrypi2@outlook.com'
    email_receiver = 'ldbraspberrypi2@outlook.com'
    currentTime = datetime.now()
    subject = currentTime.strftime("%Y.%m.%d-%H%M%S")
    
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    body = 'Text extracted using Tesseract OCR'
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(txt_file, "rb")
    part = MIMEBase('application', 'octet_stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{txt_file}"')
    msg.attach(part)

    text = msg.as_string()
    connection = smtplib.SMTP('smtp.office365.com', 587)
    connection.starttls()
    connection.login(email_sender, 'RaspberryPi')
    connection.sendmail(email_sender, email_receiver, text)
    connection.quit()
    messagebox.showinfo("Success", "Email Sent!")

# GUI Elements
capture_button = tk.Button(root, text="Capture Image", command=capture_image)
ocr_email_button = tk.Button(root, text="Perform OCR & Send Email", command=perform_ocr_send_email)
text_box = tk.Text(root, height=10, width=40)
image_label = tk.Label(root, text="Captured Image:")
image_display = tk.Label(root)

# Layout
capture_button.pack(pady=10)
ocr_email_button.pack(pady=10)
text_box.pack(pady=10)
image_label.pack()
image_display.pack(pady=10)

root.mainloop()
