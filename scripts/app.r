library(shiny)
library(shinythemes)
library(DBI)
library(RSQLite)
library(dplyr)
library(knitr)
library(kableExtra)
library(ggplot2)

# Define the path to your SQLite database
db_file_path <- "/Users/snatch./Desktop/nationwide_weather.db"

# Define UI
ui <- fluidPage(
  theme = shinytheme("sandstone"),
  titlePanel("Database Weather Data and Foreign Key Relationships"),
  
  tabsetPanel(
    tabPanel("Head", 
             sidebarLayout(
               sidebarPanel(
                 selectInput("location", "Select Location:", choices = NULL)
               ),
               mainPanel(
                 htmlOutput("filteredWeatherData")  # Updated to show filtered weather data
               )
             )),
    
    tabPanel("Foreign Key Relationships", 
             mainPanel(
               htmlOutput("dbRelationships")
             )),
    
    tabPanel("Data Overview", 
             mainPanel(
               htmlOutput("dataTypesOverview")  # Section for data types overview
             )),
    
    tabPanel("Visualizations", 
             sidebarLayout(
               sidebarPanel(
                 selectInput("graphLocation", "Select Location for Graphs:", choices = NULL),
                 selectInput("graphType", "Select Graph Type:", choices = c("All Graphs", "High Temperature Histogram", "Wind Speed Histogram", "Current Temperature Time Series"))
               ),
               mainPanel(
                 # Conditional plot rendering based on selection
                 plotOutput("selectedGraph"),
                 plotOutput("highTempHistogram", height = "400px"),
                 plotOutput("windSpeedHistogram", height = "400px"),
                 plotOutput("timeSeriesPlot", height = "400px")
               )
             ))
  )
)

# Define server logic
server <- function(input, output, session) {
  
  # Establish a connection to the SQLite database
  con <- dbConnect(RSQLite::SQLite(), dbname = db_file_path)
  
  # Load location options for the dropdowns
  observe({
    locations <- dbGetQuery(con, "SELECT DISTINCT name FROM Locations")
    updateSelectInput(session, "location", choices = locations$name)
    updateSelectInput(session, "graphLocation", choices = locations$name)
  })
  
  # Render the head of the weather data filtered by selected location
  output$filteredWeatherData <- renderUI({
    req(input$location)  # Ensure a location is selected
    
    # Load weather data and locations data
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    locations <- dbGetQuery(con, "SELECT * FROM Locations")
    
    # Clean and filter the data as before
    weather_reports <- cleanWeatherData(weather_reports)
    
    # Filter by selected location
    filtered_data <- weather_reports %>%
      inner_join(locations, by = "location_id") %>%
      filter(name == input$location) %>%
      arrange(desc(time_of_search)) %>%
      head(50)
    
    # Show the filtered data in a table
    if (nrow(filtered_data) > 0) {
      HTML(
        kable(filtered_data, "html", caption = paste("Filtered Weather Data for", input$location), escape = FALSE) %>%
          kable_styling(full_width = TRUE, position = "center") %>%
          row_spec(0, background = "#f2f2f2")
      )
    } else {
      HTML("<p>No data available for the selected location.</p>")
    }
  })
  
  # Function to render the selected graph at the top
  output$selectedGraph <- renderPlot({
    req(input$graphLocation)
    
    # Render the graph based on user selection
    if (input$graphType == "High Temperature Histogram") {
      renderHighTempHistogram()
    } else if (input$graphType == "Wind Speed Histogram") {
      renderWindSpeedHistogram()
    } else if (input$graphType == "Current Temperature Time Series") {
      renderTimeSeriesPlot()
    }
  })
  
  # Render the high temperature histogram at its default location
  output$highTempHistogram <- renderPlot({
    req(input$graphLocation)
    
    if (input$graphType == "All Graphs") {
      renderHighTempHistogram()
    }
  })
  
  # Render the wind speed histogram at its default location
  output$windSpeedHistogram <- renderPlot({
    req(input$graphLocation)
    
    if (input$graphType == "All Graphs") {
      renderWindSpeedHistogram()
    }
  })
  
  # Render the current temperature time series plot at its default location
  output$timeSeriesPlot <- renderPlot({
    req(input$graphLocation)
    
    if (input$graphType == "All Graphs") {
      renderTimeSeriesPlot()
    }
  })
  
  # Helper function to clean weather data
  cleanWeatherData <- function(weather_reports) {
    weather_reports %>%
      mutate(
        high_temperature = as.numeric(gsub("[^0-9.]", "", as.character(high_temperature))),
        wind_speed = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(wind_speed)))),
        current_temperature = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(current_temperature)))),
        time_of_search = as.POSIXct(time_of_search, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
      )
  }
  
  # Helper function to filter data by location
  filterDataByLocation <- function(weather_reports, location, con) {
    locations <- dbGetQuery(con, "SELECT * FROM Locations")
    weather_reports %>%
      inner_join(locations, by = "location_id") %>%
      filter(name == location)
  }
  
  # Function to render High Temperature Histogram
  renderHighTempHistogram <- function() {
    # Load weather data for graph
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    weather_reports <- cleanWeatherData(weather_reports)
    
    # Filter data by selected location
    filtered_data <- filterDataByLocation(weather_reports, input$graphLocation, con)
    
    # Plot histogram for high temperatures
    ggplot(filtered_data, aes(x = high_temperature)) + 
      geom_histogram(binwidth = 2, fill = "blue", color = "white") +
      labs(title = "Distribution of High Temperatures", x = "High Temperature (°C)", y = "Frequency") +
      theme_minimal()
  }
  
  # Function to render Wind Speed Histogram
  renderWindSpeedHistogram <- function() {
    # Load weather data for graph
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    weather_reports <- cleanWeatherData(weather_reports)
    
    # Filter data by selected location
    filtered_data <- filterDataByLocation(weather_reports, input$graphLocation, con)
    
    # Plot histogram for wind speed
    ggplot(filtered_data, aes(x = wind_speed)) + 
      geom_histogram(binwidth = 1, fill = "orange", color = "white") +
      labs(title = "Distribution of Wind Speed", x = "Wind Speed (km/h)", y = "Frequency") +
      theme_minimal()
  }
  
  # Function to render Time Series Plot
  renderTimeSeriesPlot <- function() {
    # Load weather data for graph
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    weather_reports <- cleanWeatherData(weather_reports)
    
    # Filter data by selected location
    filtered_data <- filterDataByLocation(weather_reports, input$graphLocation, con)
    
    # Plot time series for current temperature
    ggplot(filtered_data, aes(x = time_of_search, y = current_temperature)) +
      geom_line(color = "blue") +
      labs(title = "Current Temperature Over Time", x = "Time", y = "Current Temperature (°C)") +
      theme_minimal()
  }
  
  # Disconnect from the database when the app stops
  onStop(function() {
    dbDisconnect(con)
  })
}

# Run the application
shinyApp(ui = ui, server = server)
