provider "oci" {
  region = var.region
}

resource "oci ons_notification_topic" "grafana_alerts" {
  compartment_id = var.targetCompartment
  name           = "grafana-alerts"
  description    = "Topic for Grafana Alerts"
}

output "notification_topic_ocid" {
  value = oci_ons_notification_topic.grafana_alerts.id
}
