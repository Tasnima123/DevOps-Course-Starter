variable "location" {
    description = "The Azure location where all resources in this deployment should be created"
    default = "uksouth"
}

variable "client_id" {
    description = "The Github client id for app to be deployed on Azure"
}

variable "client_secret" {
    description = "The Github client secret for app to be deployed on Azure"
}