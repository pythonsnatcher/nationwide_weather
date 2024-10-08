library(shiny)
library(shinythemes)
library(DBI)
library(RSQLite)
library(dplyr)
library(knitr)
library(kableExtra)
library(ggplot2)
library(leaflet)

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
                 selectInput("location", "Select Location:", choices = NULL),
                 selectInput("numRows", "Number of Rows to Display:", choices = c(10, 20, 50, 100), selected = 10),
                 leafletOutput("locationMap")  # Map UI output placed in the sidebar panel
               ),
               mainPanel(
                 htmlOutput("filteredWeatherData")
               )
             )),
    
    tabPanel("Foreign Key Relationships", 
             mainPanel(
               htmlOutput("dbRelationships")
             )),
    
    tabPanel("Data Overview", 
             mainPanel(
               htmlOutput("dataTypesOverview")
             )),
    
    tabPanel("Visualizations", 
             sidebarLayout(
               sidebarPanel(
                 selectInput("graphLocation", "Select Location for Graphs:", choices = NULL),
                 selectInput("graphType", "Select Graph Type:", choices = c("All Graphs", "High Temperature Histogram", "Wind Speed Histogram", "Current Temperature Time Series")),
                 leafletOutput("visualizationsMap")  # Map UI output in the sidebar panel
               ),
               mainPanel(
                 uiOutput("graphUI")
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
  
  # Helper function to clean weather data
  cleanWeatherData <- function(weather_reports) {
    weather_reports %>%
      mutate(
        high_temperature = as.numeric(gsub("[^0-9.]", "", as.character(high_temperature))),
        wind_speed = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(wind_speed)))),
        current_temperature = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(current_temperature)))),
        low_temperature = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(low_temperature)))),
        low_tide_morning_height = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(low_tide_morning_height)))),
        high_tide_morning_height = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(high_tide_morning_height)))),
        low_tide_evening_height = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(low_tide_evening_height)))),
        high_tide_evening_height = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(high_tide_evening_height)))),
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
  
  # Render the interactive map
  renderMap <- function(location) {
    req(location)  # Ensure a location is selected
    
    # Load locations data
    locations <- dbGetQuery(con, "SELECT * FROM Locations")
    selected_location <- locations %>% filter(name == location)
    
    # Render the leaflet map
    leaflet(data = selected_location) %>%
      addTiles() %>%
      addMarkers(
        lng = ~longitude, lat = ~latitude, popup = ~name
      ) %>%
      setView(
        lng = selected_location$longitude, 
        lat = selected_location$latitude, 
        zoom = 6
      )
  }
  
  # Render the map in the "Head" tab
  output$locationMap <- renderLeaflet({
    if (!is.null(input$location)) {
      renderMap(input$location)
    }
  })
  
  # Render the map in the "Visualizations" tab
  output$visualizationsMap <- renderLeaflet({
    if (!is.null(input$graphLocation)) {
      renderMap(input$graphLocation)
    }
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
      head(as.numeric(input$numRows))  # Use the number of rows from the dropdown menu
    
    
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
  
  # Render Foreign Key Relationships
  output$dbRelationships <- renderUI({
    # Get foreign key relationships for each table
    tables <- dbListTables(con)
    fk_relationships <- lapply(tables, function(table) {
      dbGetQuery(con, paste("PRAGMA foreign_key_list(", table, ");", sep = ""))
    })
    names(fk_relationships) <- tables
    
    # Create a data frame to store relationships
    relationship_data <- do.call(rbind, lapply(names(fk_relationships), function(table) {
      df <- fk_relationships[[table]]
      if (nrow(df) > 0) {
        data.frame(
          Table = table,
          FK_Column = df$from,
          Referenced_Table = df$table,
          Referenced_Column = df$to,
          stringsAsFactors = FALSE
        )
      } else {
        NULL
      }
    }))
    
    HTML(
      kable(relationship_data, "html", caption = "Foreign Key Relationships", escape = FALSE) %>%
        kable_styling(full_width = FALSE, position = "center") %>%
        column_spec(1, bold = TRUE, color = "black") %>%
        column_spec(3, bold = TRUE, color = "black") %>%
        column_spec(2, color = "blue") %>%
        column_spec(4, color = "blue") %>%
        row_spec(0, background = "#f2f2f2")
    )
  })
  
  # Render Data Types Overview
  output$dataTypesOverview <- renderUI({
    # Load all data tables with a limit of 1 row to get schema
    tables <- c("WeatherReports", "PollutionLevels", "PollenLevels", "UVIndexLevels", "WindDirections", "Locations", "VisibilityLevels", "WeatherConditions")
    
    # Collect data types from each table
    data_types_list <- lapply(tables, function(table) {
      df <- dbGetQuery(con, paste("SELECT * FROM", table, "LIMIT 1"))
      data.frame(Column = names(df), Data_Type = sapply(df, class), stringsAsFactors = FALSE)
    })
    
    # Combine into a single output
    output_html <- ""
    for (i in seq_along(tables)) {
      table <- tables[i]
      data_types_df <- data_types_list[[i]]
      
      output_html <- paste0(output_html,
                            HTML(
                              kable(data_types_df, "html", caption = paste("Data Types for", table), escape = FALSE) %>%
                                kable_styling(full_width = FALSE, position = "center") %>%
                                column_spec(1, bold = TRUE, color = "black") %>%
                                column_spec(2, color = "blue") %>%
                                row_spec(0, background = "#f2f2f2")
                            )
      )
    }
    
    HTML(output_html)
  })
  
  # Render the selected graph
  output$graphUI <- renderUI({
    req(input$graphLocation)
    
    # Conditionally render the selected graph type
    if (input$graphType == "All Graphs") {
      tagList(
        plotOutput("highTempHistogram"),
        plotOutput("windSpeedHistogram"),
        plotOutput("timeSeriesPlot")
      )
    } else if (input$graphType == "High Temperature Histogram") {
      tagList(
        plotOutput("highTempHistogram")
      )
    } else if (input$graphType == "Wind Speed Histogram") {
      tagList(
        plotOutput("windSpeedHistogram")
      )
    } else if (input$graphType == "Current Temperature Time Series") {
      tagList(
        plotOutput("timeSeriesPlot")
      )
    }
  })
  
  # Generate graphs
  output$highTempHistogram <- renderPlot({
    req(input$graphLocation)
    
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    weather_reports <- cleanWeatherData(weather_reports)
    
    filtered_data <- filterDataByLocation(weather_reports, input$graphLocation, con)
    
    ggplot(filtered_data, aes(x = high_temperature)) +
      geom_histogram(binwidth = 1, fill = "blue", color = "black") +
      labs(title = paste("High Temperature Histogram for", input$graphLocation),
           x = "High Temperature (°C)",
           y = "Frequency")
  })
  
  output$windSpeedHistogram <- renderPlot({
    req(input$graphLocation)
    
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    weather_reports <- cleanWeatherData(weather_reports)
    
    filtered_data <- filterDataByLocation(weather_reports, input$graphLocation, con)
    
    ggplot(filtered_data, aes(x = wind_speed)) +
      geom_histogram(binwidth = 1, fill = "green", color = "black") +
      labs(title = paste("Wind Speed Histogram for", input$graphLocation),
           x = "Wind Speed (km/h)",
           y = "Frequency")
  })
  
  output$timeSeriesPlot <- renderPlot({
    req(input$graphLocation)
    
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    weather_reports <- cleanWeatherData(weather_reports)
    
    filtered_data <- filterDataByLocation(weather_reports, input$graphLocation, con)
    
    ggplot(filtered_data, aes(x = time_of_search, y = current_temperature)) +
      geom_line() +
      labs(title = paste("Current Temperature Time Series for", input$graphLocation),
           x = "Time",
           y = "Current Temperature (°C)")
  })
  
  # Disconnect from the database when the app stops
  onStop(function() {
    dbDisconnect(con)
  })
}

# Run the application
shinyApp(ui = ui, server = server)
