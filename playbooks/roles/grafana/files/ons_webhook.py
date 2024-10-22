from flask import Flask, request, jsonify, render_template_string
import oci
import json
import logging

app = Flask(__name__)

# Function to read topic OCID from file
def get_topic_ocid(file_path='/tmp/topic_ocid.txt'):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Get the topic OCID from the file
topic_id = get_topic_ocid()

# Alert template for rendering the alert message
alert_template = """
Alert: {{ alert_name }}
Status: {{ alert_status }}
{{ alert_message }}
Starts At: {{ starts_at }}
Ends At: {{ ends_at }}

Labels:
{% for key, value in labels.items() %}
{{ key }}: {{ value }}
{% endfor %}

Annotations:
{% for key, value in annotations.items() %}
{{ key }}: {{ value }}
{% endfor %}
"""

# Route to handle incoming Grafana alerts
@app.route('/grafana-webhook', methods=['POST'])
def grafana_webhook():
    try:
        config = oci.config.from_file()
        oci.config.validate_config(config)
    except oci.exceptions.ConfigFileNotFound as e:
        logging.error(f"OCI Config error: {e}")
        return jsonify({'status': 'error', 'message': 'Config error'}), 500
    
    # Initialize NotificationDataPlaneClient for OCI Notifications
    notification_client = oci.ons.NotificationDataPlaneClient(config)

    # Get the incoming alert data from the request
    alert_data = request.get_json()
    if not alert_data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    try:
        # Process each alert
        alerts = alert_data.get('alerts', [])
        for alert in alerts:
            status = alert.get('status')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            starts_at = alert.get('startsAt')
            ends_at = alert.get('endsAt')
            name = labels.get('alertname', 'No Alert Name')
            desc = annotations.get('description', 'No Description')

            # Render the alert message using the template
            alert_message = render_template_string(
                alert_template, 
                alert_name=name, 
                alert_status=status, 
                labels=labels, 
                annotations=annotations, 
                alert_message=desc, 
                starts_at=starts_at, 
                ends_at=ends_at
            )

            # Publish the formatted alert message to the OCI Notification Topic
            message_details = oci.ons.models.MessageDetails(
                title="GPU Cluster Alert",
                body=alert_message
            )
            response = notification_client.publish_message(
                topic_id=topic_id,  # Use the dynamically fetched topic_id
                message_details=message_details
            )

            logging.info(f"Message published. Message ID: {response.data.message_id}")
        
        return jsonify({'status': 'success', 'message': 'Alert processed'}), 200

    except Exception as e:
        logging.error(f"Error processing alert: {e}")
        return jsonify({'status': 'error', 'message': 'Error processing alert'}), 500

# Start the Flask app and listen on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
