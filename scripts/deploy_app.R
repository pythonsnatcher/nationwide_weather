# Ensure required packages are installed
required_packages <- c("shiny", "rsconnect", "httpuv", "rmarkdown", "knitr", "jsonlite", "RJSONIO", "htmltools", "reticulate")

new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages, repos = "https://cran.rstudio.com/")


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
