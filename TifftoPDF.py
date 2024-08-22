import datetime
from simple_salesforce import Salesforce
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import base64
import requests

class SalesforceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Salesforce TIFF to PDF Uploader")
        
        # Salesforce Credentials
        tk.Label(root, text="Username:").grid(row=0)
        tk.Label(root, text="Password:").grid(row=1)
        tk.Label(root, text="Security Token:").grid(row=2)

        self.username = tk.Entry(root)
        self.password = tk.Entry(root, show="*")
        self.security_token = tk.Entry(root)

        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        self.security_token.grid(row=2, column=1)

        # Buttons
        tk.Button(root, text='Set Credentials', command=self.set_credentials).grid(row=3, column=0, pady=4)
        tk.Button(root, text='Process TIFF Files', command=self.process_files).grid(row=3, column=1, pady=4)
        
        self.key = self.load_key()

    def load_key(self):
        key_file = "secret.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as key:
                return key.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as key_file:
                key_file.write(key)
            return key

    def set_credentials(self):
        fernet = Fernet(self.key)
        
        username_enc = fernet.encrypt(self.username.get().encode()).decode('utf-8').strip()
        password_enc = fernet.encrypt(self.password.get().encode()).decode('utf-8').strip()
        token_enc = fernet.encrypt(self.security_token.get().encode()).decode('utf-8').strip()

        with open("credentials.enc", "w") as file:
            file.write(username_enc + "\n")
            file.write(password_enc + "\n")
            file.write(token_enc + "\n")
        
        messagebox.showinfo("Info", "Credentials Encrypted and Saved Successfully!")

    
    def load_credentials(self):
        fernet = Fernet(self.key)
        with open("credentials.enc", "r") as file:
            lines = [line.strip() for line in file if line.strip()]
            username = fernet.decrypt(lines[0].encode('utf-8')).decode()
            password = fernet.decrypt(lines[1].encode('utf-8')).decode()
            token = fernet.decrypt(lines[2].encode('utf-8')).decode()
        return username.strip(), password.strip(), token.strip()



    def process_files(self):
        try:
            print('Process Started ...')
            self.download_tiff_files()
            print('All Files Downloaded ...')
            for tiff_file in os.listdir('.'):
                if tiff_file.endswith('.tiff'):
                    print('Processing Downloaded ... ' + tiff_file)
                    pdf_file = tiff_file.replace('.tiff', '.pdf')
                    self.convert_tiff_to_pdf(tiff_file, pdf_file)
                    print(' tiff_file Path --> ' + tiff_file + ' pdf_file path ' + pdf_file)
                    self.upload_pdf(pdf_file)
                    print('uploaded file  ->' + pdf_file)

                    # Delete the TIFF and PDF files after processing
                    os.remove(tiff_file)
                    os.remove(pdf_file)
                    print(f"Deleted files: {tiff_file} and {pdf_file}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def download_tiff_files(self):
        usernamer, passwordr, tokenr = self.load_credentials()
        print(usernamer, passwordr, tokenr)
        sf = Salesforce(username=usernamer, password=passwordr, security_token=tokenr)

        today = datetime.date.today().strftime("%Y-%m-%d")
        query = f"SELECT Id, Title, VersionData FROM ContentVersion WHERE FileType = 'TIFF' AND CreatedDate = TODAY"
        results = sf.query(query)
        records = results.get('records', [])

        for record in records:
            file_id = record['Id']
            print(file_id)
            file_name = record['Title']
            download_url = f"https://{sf.sf_instance}/services/data/v{sf.sf_version}/sobjects/ContentVersion/{file_id}/VersionData"
            response = requests.get(download_url, headers={'Authorization': f'Bearer {sf.session_id}'})
            
            if response.status_code == 200:
                print('Done With ')
                with open(f"{file_name}.tiff", "wb") as file:
                    file.write(response.content)
            else:
                print(f"Failed to download {file_name}.tiff")

    def convert_tiff_to_pdf(self, tiff_path, pdf_path):
        img = Image.open(tiff_path)
        c = canvas.Canvas(pdf_path, pagesize=letter)

        for i in range(img.n_frames):
            img.seek(i)
            c.drawImage(tiff_path, 0, 0, width=letter[0], height=letter[1])
            c.showPage()
        
        c.save()

    def upload_pdf(self, pdf_path):
        usernamer, passwordr, tokenr = self.load_credentials()
        print(usernamer, passwordr, tokenr)
        sf = Salesforce(username=usernamer, password=passwordr, security_token=tokenr)

        with open(pdf_path, "rb") as file:
            file_base64 = base64.b64encode(file.read()).decode('utf-8')

        content_version = {
            'Title': os.path.basename(pdf_path),
            'PathOnClient': pdf_path,
            'VersionData': file_base64,
        }

        result = sf.ContentVersion.create(content_version)

        if result['success']:
            print(f"Uploaded PDF with ContentVersion ID: {result['id']}")
        else:
            print(f"Failed to upload PDF. Error: {result['errors']}")

        

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesforceApp(root)
    root.mainloop()
