provider "oci" {
  region = var.region
}

# Create OCI Notification Topic
resource "oci_ons_notification_topic" "grafana_alerts" {
  compartment_id = var.targetCompartment
  name           = "grafana-alerts"
  description    = "Topic for Grafana Alerts"
}

# Output the notification topic OCID (for reference)
output "notification_topic_ocid" {
  value = oci_ons_notification_topic.grafana_alerts.id
}

# Write the OCID to a file using local_file
resource "local_file" "write_topic_ocid" {
  filename = "/home/opc/topic_ocid.txt"  # Replace with the absolute path
  content  = "${oci_ons_notification_topic.grafana_alerts.id}"
  }

  depends_on = [oci_ons_notification_topic.grafana_alerts]
}
