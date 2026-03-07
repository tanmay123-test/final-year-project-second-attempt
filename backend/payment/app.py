from flask import Flask, render_template
from payments.payment_route import payment_bp
from payments.webhook_handler import webhook_bp

app = Flask(__name__, template_folder='payments/templets')
app.register_blueprint(payment_bp, url_prefix="/payment")
app.register_blueprint(webhook_bp, url_prefix="/payment")

@app.route("/")
def home():
    return render_template("payment_demo.html")

if __name__ == "__main__":
    app.run(port=5001, debug=True)
