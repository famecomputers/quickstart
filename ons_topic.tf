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

resource "null_resource" "write_topic_ocid" {
  provisioner "local-exec" {
    command = "echo ${oci_ons_notification_topic.grafana_alerts.id} > /tmp/topic_ocid.txt"
  }

  depends_on = [oci_ons_notification_topic.grafana_alerts]
}
