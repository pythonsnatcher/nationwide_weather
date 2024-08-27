library(shiny)
library(shinythemes)
library(DBI)
library(RSQLite)
library(dplyr)
library(knitr)
library(kableExtra)

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
             ))
  )
)

# Define server logic
server <- function(input, output, session) {
  
  # Establish a connection to the SQLite database
  con <- dbConnect(RSQLite::SQLite(), dbname = db_file_path)
  
  # Load location options for the dropdown
  observe({
    locations <- dbGetQuery(con, "SELECT DISTINCT name FROM Locations")
    updateSelectInput(session, "location", choices = locations$name)
  })
  
  # Render the head of the weather data filtered by selected location
  output$filteredWeatherData <- renderUI({
    req(input$location)  # Ensure a location is selected
    
    # Load weather data and locations data
    weather_reports <- dbGetQuery(con, "SELECT * FROM WeatherReports")
    locations <- dbGetQuery(con, "SELECT * FROM Locations")
    
    # Debug: Print the first few rows of the weather_reports to check data types
    print(head(weather_reports))
    
    # Convert time_of_search to POSIXct
    if ("time_of_search" %in% colnames(weather_reports)) {
      # Check for the correct format
      weather_reports$time_of_search <- as.POSIXct(weather_reports$time_of_search, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
      
      # Debug: Print the structure of the time_of_search column to confirm conversion
      print(str(weather_reports$time_of_search))
    } else {
      print("time_of_search column not found")
    }
    
    # Clean numeric columns
    weather_reports <- weather_reports %>%
      mutate(
        high_temperature = as.numeric(gsub("[^0-9.]", "", as.character(high_temperature))),
        low_temperature = as.numeric(gsub("[^0-9.]", "", as.character(low_temperature))),
        current_temperature = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(current_temperature)))),
        wind_speed = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(wind_speed)))),
        humidity = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(humidity)))),
        chance_of_precipitation = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(chance_of_precipitation)))),
        pressure = suppressWarnings(as.numeric(gsub("[^0-9.]", "", as.character(pressure))))
      )
    
    # Filter out rows with 'wind_speed' values above 38
    weather_reports <- weather_reports %>%
      filter(wind_speed <= 38)
    
    # Extract date from time_of_search
    weather_reports$date <- as.Date(weather_reports$time_of_search)
    
    # Find the minimum low_temperature for each day
    daily_min_low_temp <- weather_reports %>%
      group_by(date) %>%
      summarise(min_low_temp = min(low_temperature[low_temperature > 0], na.rm = TRUE))
    
    # Join the daily minimum low temperature back to the original data
    weather_reports <- weather_reports %>%
      left_join(daily_min_low_temp, by = "date")
    
    # Replace 0 and NA low_temperature values with the daily minimum low temperature
    weather_reports <- weather_reports %>%
      mutate(
        low_temperature = ifelse(is.na(low_temperature) | low_temperature == 0, min_low_temp, low_temperature)
      )
    
    # Remove the temporary min_low_temp column
    weather_reports <- weather_reports %>%
      select(-min_low_temp)
    
    # Filter by selected location
    filtered_data <- weather_reports %>%
      inner_join(locations, by = "location_id") %>%
      filter(name == input$location) %>%
      arrange(desc(time_of_search)) %>%
      head(50)
    
    
    
    # Show the first few rows of the filtered data
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
  
  # Render the data types after cleaning
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
      
      # Add table header and horizontal line for separation
      if (i > 1) {
        output_html <- paste0(output_html, "<hr>")
      }
      
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
  
  
  # Render the foreign key relationships
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
  
  # Disconnect from the database when the app stops
  onStop(function() {
    dbDisconnect(con)
  })
}

# Run the application
shinyApp(ui = ui, server = server)
