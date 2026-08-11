variable "aws_region" { type = string }
variable "state_bucket_name" { type = string }
variable "lock_table_name" {
  type    = string
  default = "lumens-terraform-lock"
}
variable "name_prefix" {
  type    = string
  default = "lumens"
}
variable "github_repository" {
  type        = string
  description = "owner/repository"
}
