# 📝 Flask Blogging Website

A full-featured blogging website built with **Flask** and **Bootstrap**, featuring user authentication, role-based access control, and blog interaction features.  

🔗 **Live Demo:** [https://flask-blogging-platform-cjav.onrender.com](https://flask-blogging-platform-cjav.onrender.com)

## ✨ Features
- **User Authentication** → Register, Login, Logout  
- **Role-Based Access Control**  
  - **Admin**: Can Create, Edit, and Delete blog posts  
  - **Normal Users**: Can view posts, add comments, and contact the admin  
- **Blog Features**  
  - Add and view comments on blog posts  
  - Navigate to older posts for easy browsing  
- Responsive design with **Bootstrap**  
- Contact admin directly via email  
- SQLite database for local development  
- PostgreSQL database for production deployment  

## 🛠 Tech Stack
- **Backend:** Flask (Python 3.12.5)  
- **Frontend:** HTML, CSS, Bootstrap  
- **Database:** SQLite (local) / PostgreSQL (deployed)  
- **Templating Engine:** Jinja2  

## 🚀 Getting Started

### Prerequisites
- Python **3.12.5**  
- Virtual environment (recommended)  

### Installation
1. Clone the repository
```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
  ```
2. Create & activate a virtual environment
  ```bash
  python -m venv venv
  source venv/bin/activate   # On Mac/Linux
  venv\Scripts\activate      # On Windows
```
3. Install dependencies
  ```bash
https://github.com/user-attachments/assets/b4c64e6c-24a0-40ef-ba00-4e40193c7fdf

  pip install -r requirements.txt
```
4. Run the app
  ```bash
  python dev.py
```
5. Open in your browser:
http://127.0.0.1:5000

### 📌 Future Improvements
1. Add categories/tags for blog posts
2. Improve comment system (nested replies, likes)
3. Add user profile pages
