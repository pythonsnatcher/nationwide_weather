# Ensure system dependencies are available
system("sudo apt-get update")
system("sudo apt-get install -y libcurl4-openssl-dev")

# Install the 'rsconnect' package if it's not already installed
if (!requireNamespace("rsconnect", quietly = TRUE)) {
  install.packages("rsconnect", repos = "https://cran.rstudio.com/")
}

# Load the rsconnect package
library(rsconnect)

# Set account information
rsconnect::setAccountInfo(
  name = 'tuco-bear',  # Replace with your ShinyApps.io account name
  token = Sys.getenv("SHINYAPPS_TOKEN"),
  secret = Sys.getenv("SHINYAPPS_SECRET")
)

# Deploy the app
rsconnect::deployApp(
  appDir = "scripts",      # Path to your app directory
  appFiles = c("app.r"),   # Ensure this includes all necessary files for deployment
  appName = "your-app-name",  # Replace with your app name
  forceUpdate = TRUE
)
