# import dependencies
from flask import Flask, render_template
import pymongo
import scrape_mars

# create instance of Flask app
app = Flask(__name__)

# create mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def home():
    mars_data = mongo.db.mars.find_one()
    return  render_template('index.html', mars_data=mars_data)

@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape_all()
    mars.update({}, mars_data, upsert=True)
    return "Scraping Successful!"


if __name__ == "__main__":
    app.run()
