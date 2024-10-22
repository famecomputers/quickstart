provider "oci" {
  region = var.region
}

resource "oci_ons_notification_topic" "grafana_alerts" {
  compartment_id = var.targetCompartment
  name           = "grafana-alerts"
  description    = "Topic for Grafana Alerts"
}

output "notification_topic_ocid" {
  value = oci_ons_notification_topic.grafana_alerts.id
}

# Use local-exec to set an environment variable and write the OCID to a file
resource "null_resource" "write_topic_ocid" {
  provisioner "local-exec" {
    # Set environment variable for the topic OCID
    environment = {
      TOPIC_OCID = "${oci_ons_notification_topic.grafana_alerts.id}"
    }

    # Use the environment variable to write the OCID to a file
    command = "echo $TOPIC_OCID > $HOME/topic_ocid.txt && chmod 600 $HOME/topic_ocid.txt"
  }

  depends_on = [oci_ons_notification_topic.grafana_alerts]
}
