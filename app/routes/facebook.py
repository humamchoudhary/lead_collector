import os
from flask import Blueprint, request, jsonify

fb_bp = Blueprint("facebook", __name__,url_prefix="/fb")



FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN', 'your_fb_verify_token_here')

@fb_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for Facebook Messenger"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("Facebook webhook verified successfully!")
        return challenge, 200
    print("Facebook webhook verification failed!")
    return "Forbidden", 403


@fb_bp.route("/webhook",methods=["POST"])
def webhook_sub():
    data = request.get_json()
    print(data)
    return 200

