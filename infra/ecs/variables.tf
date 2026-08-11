variable "aws_region" { type = string }
variable "name_prefix" {
  type    = string
  default = "lumens"
}
variable "image_tag" {
  type    = string
  default = "latest"
}
variable "dynatrace_headers_secret_name" {
  type    = string
  default = "lumens/dynatrace/otlp-headers"
}
variable "dynatrace_otlp_endpoint" {
  type        = string
  description = "Dynatrace OTLP HTTP endpoint without credentials"
}
variable "tags" {
  type    = map(string)
  default = {}
}
