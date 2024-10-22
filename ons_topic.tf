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

resource "local_file" "write_topic_ocid" {
  filename = "/tmp/topic_ocid.txt"
  content  = "${oci_ons_notification_topic.grafana_alerts.id}"

  provisioner "local-exec" {
    command = "chmod 644 /tmp/topic_ocid.txt"
  }
  depends_on = [oci_ons_notification_topic.grafana_alerts]
}
