# Set CRAN mirror to avoid issues with package installation
cran_mirror <- "https://cran.rstudio.com/"

# Install the 'rsconnect' package if it's not already installed
if (!requireNamespace("rsconnect", quietly = TRUE)) {
  install.packages("rsconnect", repos = cran_mirror)
}

# Load the package
library(rsconnect)

# Set account information
rsconnect::setAccountInfo(
  name = 'tuco-bear',  # Replace with your ShinyApps.io account name
  token = Sys.getenv("SHINYAPPS_TOKEN"),
  secret = Sys.getenv("SHINYAPPS_SECRET")
)

# Deploy the app
rsconnect::deployApp(
  appDir = "scripts",      # Replace with the path to your app directory
  appFiles = c("app.r"),   # Ensure this includes all necessary files for deployment
  appName = "your-app-name",  # Replace with your app name
  forceUpdate = TRUE
)
