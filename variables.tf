variable "location" {
    description = "The Azure location where all resources in this deployment should be created"
    default = "uksouth"
}

variable "client_id" {
    description = "The Github client id for app to be deployed on Azure"
    default="a45ffa103c2c613d4b45"
}

variable "client_secret" {
    description = "The Github client secret for app to be deployed on Azure"
    default="150fb9c8e93fc2ea35fc1b0431336802af8454ba"
}