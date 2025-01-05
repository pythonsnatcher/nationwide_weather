# Load the rsconnect package
if (!require("rsconnect")) {
  install.packages("rsconnect", repos = "https://cran.rstudio.com/")
}
library(rsconnect)

# Set account information
rsconnect::setAccountInfo(
  name = 'tuco-bear',
  token = Sys.getenv("SHINYAPPS_TOKEN"),
  secret = Sys.getenv("SHINYAPPS_SECRET")
)

# Deploy the app
rsconnect::deployApp(
  appDir = "scripts",
  appFiles = c("app.r"),
  appName = "your-app-name",
  forceUpdate = TRUE
)
