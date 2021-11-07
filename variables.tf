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

variable "LOGGLY_TOKEN" {
    description = "Token to send logs to Loggly"
    default="9ca99023-eaf4-484a-ae0d-7b56a842a424"
}

