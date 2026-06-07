from werkzeug.security import generate_password_hash, check_password_hash
from .models.user import db, User
from .models.driver import Driver
from flask import Flask, render_template, request, redirect, url_for, flash
def checklogin(username, password, role):
    user_obj = User.query.filter_by(email=username).first()
    
    # 1. Check if user exists
    if not user_obj:
        print("Login failed: User not found")
        return False
        
    # 2. Verify password
    if not check_password_hash(user_obj.password, password):
        print("Login failed: Incorrect password")
        return False

    # 3. Check Role (1 for user, 2 for driver)
    required_role = 1 if role == "user" else 2
    
    if user_obj.role == required_role:
        print(f"Login ({role}) successful for: {user_obj.name}")
        return True
    else:
        print(f"Login failed: Role mismatch. Expected {role}")
        return False
    
def signup(name,email,password,role):
    # Check if user already exists
    new_user = None
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("User already exists")
        return False
    
            # Hash the password
    hashed_password = generate_password_hash(password)
            
            # Create new user
    if(role=="user"):
        new_user = User(name=name, email=email, password=hashed_password,role=1)
    else:
        new_user= User(name=name,email=email,password=hashed_password,role=2)
        
    try:
        db.session.add(new_user)
        db.session.commit()
        print(f"User created successfully: {new_user}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return False
def forgot_password(email):
    user_obj = User.query.filter_by(email=email).first()
    if user_obj:
        print(f"Password reset link sent to: {email}")
        return True
    else:
        print("Email not found")
        return False