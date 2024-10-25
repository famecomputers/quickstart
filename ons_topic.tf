provider "oci" {
  region = var.region
}

resource "oci_ons_notification_topic" "grafana_alerts" {
  compartment_id = var.targetCompartment
  name           = "grafana-alerts"
  description    = "Topic for Grafana Alerts"
}



