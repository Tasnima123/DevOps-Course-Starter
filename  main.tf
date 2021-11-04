terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = ">= 2.49"
            }
        }
}
provider "azurerm" {
    features {}
}
data "azurerm_resource_group" "main" {
    name = "CreditSuisse2_TasnimaMiah_ProjectExercise"
}
resource "azurerm_app_service_plan" "main" {
    name = "terraformed-asp"
    location = data.azurerm_resource_group.main.location
    resource_group_name = data.azurerm_resource_group.main.name
    kind = "Linux"
    reserved = true
    sku {
        tier = "Basic"
        size = "B1"
    }
}
resource "azurerm_app_service" "main" {
    name = "devops-todo-app"
    location = data.azurerm_resource_group.main.location
    resource_group_name = data.azurerm_resource_group.main.name
    app_service_plan_id = azurerm_app_service_plan.main.id
    site_config {
        app_command_line = ""
        linux_fx_version = "DOCKER|tasnimamiah/my-test-image:latest"
    }
    app_settings = {
        "DOCKER_REGISTRY_SERVER_URL" = "https://index.docker.io"
        "MONGODB_CONNECTION_STRING" = "mongodb://${azurerm_cosmosdb_account.tasnimamiah.name}:${azurerm_cosmosdb_account.tasnimamiah.primary_key}@${azurerm_cosmosdb_account.tasnimamiah.name}.mongo.cosmos.azure.com:10255/DefaultDatabase?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@tasnimamiah@"
        "SECRET_KEY"="secret-key"
        "MONGO_COLLECTION"="todos"
        "client_id"=var.client_id
        "client_secret"=var.client_secret
        "disable_login"="False"
        "redirect_uri"="https://devops-todo-app.azurewebsites.net/login/"
        "FLASK_APP"="todo_app/app"
        "FLASK_ENV"="development"
        "FLASK_SKIP_DOTENV"="True"
    }
}

resource "azurerm_cosmosdb_account" "tasnimamiah" {
  name = "tasnimamiah"
  resource_group_name = "CreditSuisse2_TasnimaMiah_ProjectExercise"
  offer_type = "Standard"
  kind = "MongoDB"
  location = "UK South"

  geo_location {
    location = var.location
    failover_priority = 0
  }
  consistency_policy {
    consistency_level  = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix = 100
  }
  capabilities {
    name = "EnableServerless"
  }
   capabilities {
    name = "EnableMongo"
  }
}

resource "azurerm_cosmosdb_mongo_database" "main" {
    name = "project_exercise"
    resource_group_name = azurerm_cosmosdb_account.tasnimamiah.resource_group_name
    account_name = azurerm_cosmosdb_account.tasnimamiah.name
    lifecycle { prevent_destroy = true } 
}

resource "azurerm_cosmosdb_mongo_collection" "main" {
  name                = "todos"
  resource_group_name = azurerm_cosmosdb_account.tasnimamiah.resource_group_name
  account_name        = azurerm_cosmosdb_account.tasnimamiah.name
  database_name       = azurerm_cosmosdb_mongo_database.main.name
  index {
      keys = [
        "_id"
      ]
      unique = true
  }
}