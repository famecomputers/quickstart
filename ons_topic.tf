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

# Use local_file to write the OCID to a file
resource "local_file" "write_topic_ocid" {
  filename = "$HOME/topic_ocid.txt"  # You can replace this with an absolute path if needed
  content  = "${oci_ons_notification_topic.grafana_alerts.id}"  # Write the OCID to the file

  # Optionally, set permissions after file creation (manual step if necessary)
  provisioner "local-exec" {
    command = "chmod 600 $HOME/topic_ocid.txt"
  }

  depends_on = [oci_ons_notification_topic.grafana_alerts]
}
