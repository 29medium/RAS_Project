from flask import Blueprint, render_template, request, jsonify, redirect
import logging

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")
    



