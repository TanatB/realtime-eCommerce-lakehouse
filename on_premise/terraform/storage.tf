locals {
    bucket_prefix = "${var.project_id}-lakehouse"

    # Define all medallion layers
    data_layers = {
        landing = "Raw event data landing zone from Kafka"
        bronze = "Raw data preserved in Delta Lake format"
        silver = "Cleaned, validated, and conformed data"
        gold = "Business-level aggregations and star schema"
        checkpoints = "Spark Structured Streaming checkpoints"
    }
}

resource "google_storage_bucket" "data_layers" {
  for_each = local.data_layers

  name = "${local.bucket_prefix}-${each.key}-${var.environment}"
  location = var.region

  # Use standard storage class for active data
  storage_class = "STANDARD"

  # Uniform bucket-level access (recommended over ACLs)
  uniform_bucket_level_access = true

  # Prevent accidental deletion in Terraform
  # Set to false when you actually want to destroy
  force_destroy = var.environment == "dev" ? true : false

  # Lifecycle rule: move old data to cheaper storage
  dynamic "lifecycle_rule" {
    # Only apply lifecycle rules to bronze/silver
    for_each = contains(["bronze", "silver"], each.key) ? [1] : []
    content {
      action {
        type = "SetStorageClass"
        storage_class = "NEARLINE"
      }
      condition {
        age = 90 # move to Nearline after 90 days
      }
    }
  }
  
  labels = {
    environment = var.environment
    layer = each.key
    project = "ecommerce-lakehouse"
    managed_by = "terraform"
    }
}