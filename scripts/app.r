options(repos = c(CRAN = "https://cloud.r-project.org"))

install.packages(c(
  "DBI",
  "RPostgres",
  "shiny",
  "plotly",
  "dplyr",
  "leaflet",
  "shinyjs",
  "RSQLite",
  "lubridate",
  "dotenv",
  "terra" 
))
# Load required libraries
library(DBI)
library(RPostgres)
library(shiny)
library(plotly)
library(dplyr)
library(leaflet)
library(shinyjs)
library(RSQLite)
library(dotenv)


# Construct the PostgreSQL URL using the API key from environment variables
DATABASE_URL <- sprintf(
  "postgresql://8sc131:%s@eu-west-1.sql.xata.sh/nationwide_weather:main?sslmode=require",
  Sys.getenv("XATA_API_KEY")
)

# Data loading function to query from PostgreSQL
query_weather_data <- function() {
  # Set up connection using environment variables
  conn <- dbConnect(
    RPostgres::Postgres(),
    host = "eu-west-1.sql.xata.sh",
    port = 5432,
    user = "8sc131",
    password = Sys.getenv("XATA_API_KEY"),
    dbname = "nationwide_weather:main",
    sslmode = "require"
  )

  # ... existing code ...



  
  # Query to fetch the weather data from the PostgreSQL database
  query <- "
    SELECT
      wr.*,
      wc.description AS weather_condition,
      vl.description AS visibility_description,
      loc.name AS location_name,
      wd.description AS wind_direction_description,
      uv.level AS uv_index_level,
      pl.level AS pollen_level,
      pol.level AS pollution_level
    FROM
      WeatherReports wr
    LEFT JOIN WeatherConditions wc ON wr.weather_condition_id = wc.weather_condition_id
    LEFT JOIN VisibilityLevels vl ON wr.visibility_id = vl.visibility_id
    LEFT JOIN Locations loc ON wr.location_id = loc.location_id
    LEFT JOIN WindDirections wd ON wr.wind_direction_id = wd.wind_direction_id
    LEFT JOIN UVIndexLevels uv ON wr.uv_index_id = uv.uv_index_id
    LEFT JOIN PollenLevels pl ON wr.pollen_id = pl.pollen_id
    LEFT JOIN PollutionLevels pol ON wr.pollution_id = pol.pollution_id
    order by time_of_search desc
    --limit 10
  "

  
  # Fetch the data
  df <- dbGetQuery(conn, query)

  # Disconnect from the PostgreSQL database
  dbDisconnect(conn)

  return(df)
}

# Query data from PostgreSQL
df <- query_weather_data()

# Check if data is loaded successfully
if (nrow(df) == 0) {
  stop("No data fetched from the database.")
} else {
  print("Data successfully loaded from PostgreSQL.")
}

library(lubridate)

# Example column conversion: Sunset, Sunrise, Low Tide, etc.
# Convert 'sunset' and 'sunrise' to time-only (h:m:s) format
df$sunset <- format(as.POSIXct(df$sunset, origin = "1970-01-01", tz = "UTC"), "%H:%M:%S")
df$sunrise <- format(as.POSIXct(df$sunrise, origin = "1970-01-01", tz = "UTC"), "%H:%M:%S")
# Convert tide times to time-only (h:m:s) format
df$low_tide_morning_time <- format(as.POSIXct(df$low_tide_morning_time, origin = "1970-01-01", tz = "UTC"), "%H:%M:%S")
df$high_tide_morning_time <- format(as.POSIXct(df$high_tide_morning_time, origin = "1970-01-01", tz = "UTC"), "%H:%M:%S")
df$low_tide_evening_time <- format(as.POSIXct(df$low_tide_evening_time, origin = "1970-01-01", tz = "UTC"), "%H:%M:%S")
df$high_tide_evening_time <- format(as.POSIXct(df$high_tide_evening_time, origin = "1970-01-01", tz = "UTC"), "%H:%M:%S")


# Handling missing or invalid times
df$sunset <- ifelse(is.na(df$sunset), NA, df$sunset)
df$sunrise <- ifelse(is.na(df$sunrise), NA, df$sunrise)
df$low_tide_morning_time <- ifelse(is.na(df$low_tide_morning_time), NA, df$low_tide_morning_time)
df$high_tide_morning_time <- ifelse(is.na(df$high_tide_morning_time), NA, df$high_tide_morning_time)
df$low_tide_evening_time <- ifelse(is.na(df$low_tide_evening_time), NA, df$low_tide_evening_time)
df$high_tide_evening_time <- ifelse(is.na(df$high_tide_evening_time), NA, df$high_tide_evening_time)
df$time_of_search <- as.POSIXct(df$time_of_search, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
# Add latitude and longitude to the data frame
location_coords <- data.frame(
  location_name = c("London", "Birmingham", "Manchester", "Nottingham", "Leeds", "Liverpool", "Bristol", "Newcastle upon Tyne", "Southampton", "Brighton"),
  latitude = c(51.5074, 52.4862, 53.4839, 52.9548, 53.8008, 53.4084, 51.4545, 54.9783, 50.9097, 50.8225),
  longitude = c(-0.1278, -1.8904, -2.2446, -1.1581, -1.5491, -2.9916, -2.5879, -1.6174, -1.4044, -0.1372)
)

df <- left_join(df, location_coords, by = "location_name")

# Define the UI for the Shiny app
ui <- fluidPage(
  useShinyjs(),  # Enable shinyjs for modal
  tags$head(
    tags$style(HTML("
        body {
          background: linear-gradient(270deg, #66b3ff, #ffffff);
          background-size: 400% 400%;
          -webkit-animation: gradientAnimation 30s ease infinite;
          animation: gradientAnimation 30s ease infinite;
          padding: 20px;
        }
        .container-fluid {
          margin-bottom: 30px;
        }
        .well {
          margin-bottom: 20px;
        }
        @keyframes gradientAnimation {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        /* Reduce size of Leaflet control buttons (+/-) */
        .leaflet-control-zoom-in,
        .leaflet-control-zoom-out {
          width: 20px;
          height: 20px;
          font-size: 14px;
        }
        /* Customize plotly legends */
        .plotly .legend {
          font-size: 16px;
          font-weight: bold;
        }
        /* Customize buttons */
        .btn-primary {
          background-color: #007bff;
          border-color: #007bff;
        }
        .btn-primary:hover {
          background-color: #0056b3;
          border-color: #0056b3;
        }
      "))
  ),

  h2("English Weather Stats", style = "margin-bottom: 40px; text-align: center; color: #333; font-weight: 600;"),

  sidebarLayout(
    sidebarPanel(
      h4("Filter Options"),
      selectInput("location_filter", "Select Location:", choices = sort(unique(df$location_name)), selected = "London"),
      sliderInput("date_range", "Select Date Range:",
            min = min(df$time_of_search, na.rm = TRUE),
            max = max(df$time_of_search, na.rm = TRUE),
            value = c(max(df$time_of_search, na.rm = TRUE) - months(2),
                     max(df$time_of_search, na.rm = TRUE)),
            timeFormat = "%Y-%m-%d"),
      actionButton("apply_filter", "Reset Filter", class = "btn btn-primary", style = "margin-top: 20px;"),

      h4("Location Map", style = "margin-top: 30px;"),
      leafletOutput("map", height = "300px"),
      width = 3
    ),

    mainPanel(
      fluidRow(
        column(12,
               downloadButton('downloadData', 'Download Filtered Data (CSV)'),
               br(),
               br()  # Add some space after the button
        )
      ),
      fluidRow(
        column(12,
               wellPanel(
                 style = "padding: 0;",
                 actionButton("toggleRawData", "Raw Data ▼", 
                            style = "width: 100%; text-align: left; padding: 10px;"),
                 shinyjs::hidden(
                   div(id = "rawDataContent",
                       div(style = 'overflow-x: scroll; overflow-y: scroll; max-height: 400px; background-color: white; padding: 15px; border-radius: 5px;',
                           uiOutput("csv_scroller")
                       )
                   )
                 )
               )
        ),
        br()
      ),
      fluidRow(
        column(12, 
               h4("Temperature Over Time"),
               plotlyOutput("temperature_plot")),
        br()
      ),
      fluidRow(
        column(12, 
               h4("Temperature vs Chance of Precipitation"),
               plotlyOutput("humidity_precip_plot")),
        br()
      ),
      fluidRow(
        column(6,
               h4("Wind Direction Distribution"),
               plotlyOutput("wind_rose")),
        column(6,
               h4("Wind Speed by Direction"),
               plotlyOutput("wind_speed_rose")),
        br()
      ),
      fluidRow(
        column(12, 
               h4("Humidity vs Temperature"),
               plotlyOutput("humidity_temp_plot")),
        br()
      ),
      fluidRow(
        column(12, 
               h4("Weather Condition Distribution"),
               plotlyOutput("weather_condition_histogram")),
        br()
      )
    )
  )
)
# Define the server logic

server <- function(input, output, session) {

  parse_wind_direction <- function(direction_text) {
    # Convert to lowercase
    text <- tolower(direction_text)

    # Remove all words except directional terms
    text <- gsub("light|moderate|strong|winds|from|the", "", text)
    text <- trimws(text)  # Remove extra whitespace

    # Define direction mapping
    direction_map <- list(
      "north" = 0,
      "north east" = 45,
      "northeast" = 45,
      "east" = 90,
      "south east" = 135,
      "southeast" = 135,
      "south" = 180,
      "south west" = 225,
      "southwest" = 225,
      "west" = 270,
      "north west" = 315,
      "northwest" = 315
    )

    # Check for direction match
    for (dir in names(direction_map)) {
      if (grepl(dir, text)) {
        return(direction_map[[dir]])
      }
    }
    return(NA_real_)
  }

  get_filtered_data <- reactive({
    filtered_data <- df
    if (input$location_filter != "All") {
      filtered_data <- filtered_data %>% filter(location_name == input$location_filter)
    }
    filtered_data <- filtered_data %>%
      filter(time_of_search >= input$date_range[1] & time_of_search <= input$date_range[2])
    return(filtered_data)
  })

  output$csv_scroller <- renderUI({
    df_to_display <- get_filtered_data()
    tableOutput("csv_table")
  })

  output$csv_table <- renderTable({
  df_to_display <- get_filtered_data()
  df_to_display$time_of_search <- format(df_to_display$time_of_search, "%Y-%m-%d %H:%M:%S")

  # Define columns to display based on location
  columns_london <- c(
    "time_of_search", "location_name", "high_temperature", "low_temperature", "current_temperature",
    "wind_speed", "humidity", "pressure", "chance_of_precipitation", "sunset", "sunrise",
    "low_tide_morning_time", "low_tide_morning_height", "high_tide_morning_time", "high_tide_morning_height",
    "low_tide_evening_time", "low_tide_evening_height", "high_tide_evening_time", "high_tide_evening_height",
    "weather_condition", "visibility_description", "wind_direction_description", "uv_index_level",
    "pollen_level", "pollution_level"
  )

  columns_non_london <- c(
    "time_of_search", "location_name", "high_temperature", "low_temperature", "current_temperature",
    "wind_speed", "humidity", "pressure", "chance_of_precipitation", "sunset", "sunrise",
    "weather_condition", "visibility_description", "wind_direction_description", "uv_index_level",
    "pollen_level", "pollution_level"
  )

  # Select columns based on location
  columns_to_select <- if ("London" %in% df_to_display$location_name) columns_london else columns_non_london

  df_to_display %>% select(all_of(columns_to_select))
})




  output$temperature_plot <- renderPlotly({
    filtered_data <- get_filtered_data()
    plot_ly(data = filtered_data,
            x = ~time_of_search,
            y = ~current_temperature,
            type = "scatter",
            mode = "lines+markers") %>%
      layout(
        xaxis = list(title = "Time"),
        yaxis = list(
          title = "Temperature (C)"
        ),
        showlegend = FALSE
      )
  })

  # Weather Condition Histogram
  output$weather_condition_histogram <- renderPlotly({
    filtered_data <- get_filtered_data() %>%
      group_by(weather_condition) %>%
      summarise(count = n()) %>%
      filter(count >= 3) %>%
      arrange(desc(count)) %>%
      mutate(weather_condition = factor(weather_condition, levels = weather_condition))

    plot_ly(data = filtered_data,
            x = ~weather_condition,
            y = ~count,
            type = "bar") %>%
      layout(
        xaxis = list(title = "Weather Condition", tickangle = 45),
        yaxis = list(title = "Count")
      )
  })

  # Temperature vs Precipitation Plot
  output$humidity_precip_plot <- renderPlotly({
    filtered_data <- get_filtered_data() %>%
      filter(chance_of_precipitation > 0)
    
    # Create linear model for trend line
    lm_model <- lm(chance_of_precipitation ~ current_temperature, data = filtered_data)
    
    # Create sequence for trend line
    temp_range <- seq(min(filtered_data$current_temperature, na.rm = TRUE), 
                     max(filtered_data$current_temperature, na.rm = TRUE), 
                     length.out = 100)
    trend_data <- data.frame(
      current_temperature = temp_range,
      chance_of_precipitation = predict(lm_model, newdata = data.frame(current_temperature = temp_range))
    )
    
    plot_ly(
      data = filtered_data,
      x = ~current_temperature,
      y = ~chance_of_precipitation,
      type = 'scatter',
      mode = 'markers',
      marker = list(
        color = '#1f77b4',
        size = 8,
        opacity = 0.6
      ),
      showlegend = FALSE
    ) %>%
      # Add trend line
      add_trace(
        data = trend_data,
        x = ~current_temperature,
        y = ~chance_of_precipitation,
        type = 'scatter',
        mode = 'lines',
        line = list(color = 'red', width = 1),
        showlegend = FALSE,
        hoverinfo = 'skip'
      ) %>%
      layout(
        xaxis = list(
          title = "Temperature (C)",
          standoff = 30
        ),
        yaxis = list(
          title = "Chance of Precipitation (%)",
          range = c(0, 100)
        ),
        showlegend = FALSE,
        hovermode = "closest"
      )
  })

  # Wind Direction Distribution
  output$wind_rose <- renderPlotly({
    filtered_data <- get_filtered_data()
    
    # Function to convert wind description to angle
    get_angle <- function(description) {
      if (is.na(description) || !is.character(description)) {
        return(NA)
      }
      
      # Remove "wind from" and convert to lowercase
      direction <- tolower(trimws(description))
      
      # Define cardinal direction angles (angle where wind is pointing TO)
      # Adjusted to match compass degrees (0 = North, 90 = East, etc.)
      angles <- c(
        "north" = 0,    # Changed from 180
        "south" = 180,  # Changed from 0
        "east" = 90,    # Changed from 270
        "west" = 270    # Changed from 90
      )
      
      # Count occurrences of each direction
      n_count <- as.integer(grepl("north", direction))
      s_count <- as.integer(grepl("south", direction))
      e_count <- as.integer(grepl("east", direction))
      w_count <- as.integer(grepl("west", direction))
      
      # Calculate weighted average angle
      total_weight <- n_count + s_count + e_count + w_count
      if (total_weight == 0 || is.na(total_weight)) {
        return(NA)
      }
      
      weighted_angle <- (
        n_count * angles["north"] +
        s_count * angles["south"] +
        e_count * angles["east"] +
        w_count * angles["west"]
      ) / total_weight
      
      return(weighted_angle)
    }
    
    wind_freq <- filtered_data %>%
      mutate(angle = sapply(wind_direction_description, get_angle)) %>%
      filter(!is.na(angle)) %>%
      group_by(angle) %>%
      summarise(
        count = n(),
        descriptions = list(unique(wind_direction_description)),
        .groups = 'drop'
      )

    # Print to console
    cat("\nWind Direction Frequencies:\n")
    cat("------------------------\n")
    wind_freq %>%
      arrange(desc(count)) %>%
      mutate(
        angle_readable = case_when(
          angle == 0 ~ "North",
          angle == 90 ~ "East",
          angle == 180 ~ "South",
          angle == 270 ~ "West",
          TRUE ~ sprintf("%.1f degrees", angle)
        )
      ) %>%
      rowwise() %>%
      mutate(desc_str = paste(unlist(descriptions), collapse = ", ")) %>%
      select(angle_readable, count, desc_str) %>%
      print(n = Inf)
    cat("------------------------\n")

    plot_ly(data = wind_freq,
            type = 'barpolar',
            r = ~count,
            theta = ~angle) %>%
      layout(
        polar = list(
          angularaxis = list(
            direction = "clockwise",
            rotation = 90,  # Changed from 270 to 90 to put North at top
            ticktext = c("N", "", "NE", "", "E", "", "SE", "", 
                        "S", "", "SW", "", "W", "", "NW", ""),
            tickvals = seq(0, 337.5, 22.5)
          )
        ),
        showlegend = FALSE
      )
  })

  # Wind Speed by Direction
  output$wind_speed_rose <- renderPlotly({
    filtered_data <- get_filtered_data()
    
    # Reuse the same get_angle function from above
    get_angle <- function(description) {
      if (is.na(description) || !is.character(description)) {
        return(NA)
      }
      
      direction <- tolower(trimws(description))
      
      angles <- c(
        "north" = 0,
        "south" = 180,
        "east" = 90,
        "west" = 270
      )
      
      n_count <- as.integer(grepl("north", direction))
      s_count <- as.integer(grepl("south", direction))
      e_count <- as.integer(grepl("east", direction))
      w_count <- as.integer(grepl("west", direction))
      
      total_weight <- n_count + s_count + e_count + w_count
      if (total_weight == 0 || is.na(total_weight)) {
        return(NA)
      }
      
      weighted_angle <- (
        n_count * angles["north"] +
        s_count * angles["south"] +
        e_count * angles["east"] +
        w_count * angles["west"]
      ) / total_weight
      
      return(weighted_angle)
    }
    
    wind_speed_avg <- filtered_data %>%
      mutate(angle = sapply(wind_direction_description, get_angle)) %>%
      filter(!is.na(angle)) %>%
      group_by(angle) %>%
      summarise(
        avg_speed = mean(wind_speed, na.rm = TRUE),
        descriptions = list(unique(wind_direction_description)),
        .groups = 'drop'
      )

    # Print to console
    cat("\nWind Speed Averages by Direction:\n")
    cat("------------------------\n")
    wind_speed_avg %>%
      arrange(desc(avg_speed)) %>%
      mutate(
        angle_readable = case_when(
          angle == 0 ~ "North",
          angle == 90 ~ "East",
          angle == 180 ~ "South",
          angle == 270 ~ "West",
          TRUE ~ sprintf("%.1f degrees", angle)
        )
      ) %>%
      rowwise() %>%
      mutate(
        desc_str = paste(unlist(descriptions), collapse = ", "),
        avg_speed = round(avg_speed, 1)
      ) %>%
      select(angle_readable, avg_speed, desc_str) %>%
      print(n = Inf)
    cat("------------------------\n")

    plot_ly(data = wind_speed_avg,
            type = 'barpolar',
            r = ~avg_speed,
            theta = ~angle) %>%
      layout(
        polar = list(
          angularaxis = list(
            direction = "clockwise",
            rotation = 90,
            ticktext = c("N", "", "NE", "", "E", "", "SE", "", 
                        "S", "", "SW", "", "W", "", "NW", ""),
            tickvals = seq(0, 337.5, 22.5)
          )
        ),
        showlegend = FALSE
      )
  })

  output$map <- renderLeaflet({
    filtered_data <- get_filtered_data()
    leaflet(data = filtered_data) %>%
      addTiles() %>%
      addCircleMarkers(~longitude, ~latitude, popup = ~location_name, radius = 8, color = "blue", opacity = 0.7, fillOpacity = 0.6)
  })

  observeEvent(input$apply_filter, {
    updateSliderInput(session, "date_range", value = c(min(df$time_of_search), max(df$time_of_search)))
    updateSelectInput(session, "location_filter", selected = "All")
  })

  # Show the modal with instructions on the first run
  observe({
    showModal(modalDialog(
      title = "Welcome to the Weather App",
      "This app provides interactive plots of weather data. You can filter by location and date.
      Use the Plotly graphs' interactive features like zoom, hover, and click-drag to explore the data further.",
      easyClose = TRUE,
      footer = NULL
    ))
  })

  output$humidity_temp_plot <- renderPlotly({
    filtered_data <- get_filtered_data() %>%
      filter(!is.na(current_temperature), !is.na(humidity))
    
    # Create linear model for trend line
    lm_model <- lm(humidity ~ current_temperature, data = filtered_data)
    
    # Create sequence for trend line
    temp_range <- seq(min(filtered_data$current_temperature, na.rm = TRUE), 
                     max(filtered_data$current_temperature, na.rm = TRUE), 
                     length.out = 100)
    trend_data <- data.frame(
      current_temperature = temp_range,
      humidity = predict(lm_model, newdata = data.frame(current_temperature = temp_range))
    )
    
    # Create scatter plot
    p <- plot_ly(data = filtered_data,
            x = ~current_temperature,
            y = ~humidity,
            type = 'scatter',
            mode = 'markers',
            marker = list(
              color = '#1f77b4',
              size = 8,
              opacity = 0.6
            ),
            showlegend = FALSE) %>%
      # Add trend line
      add_trace(
        data = trend_data,
        x = ~current_temperature,
        y = ~humidity,
        type = 'scatter',
        mode = 'lines',
        line = list(color = 'red'),
        showlegend = FALSE
      ) %>%
      layout(
        xaxis = list(
          title = "Temperature (C)",
          standoff = 30
        ),
        yaxis = list(
          title = "Humidity (%)",
          range = c(0, 100)
        ),
        showlegend = FALSE,
        hovermode = "closest"
      )
    
    # Print correlation coefficient to console
    cor_value <- cor(filtered_data$current_temperature, filtered_data$humidity)
    cat("\nCorrelation between Temperature and Humidity:\n")
    cat("------------------------\n")
    cat("Correlation coefficient:", round(cor_value, 3), "\n")
    cat("------------------------\n")
    
    p
  })

  output$downloadData <- downloadHandler(
    filename = function() {
      paste("weather_data_", format(Sys.time(), "%Y%m%d_%H%M"), ".csv", sep="")
    },
    content = function(file) {
      # Get the filtered data
      data_to_download <- get_filtered_data()
      write.csv(data_to_download, file, row.names = FALSE)
    }
  )

  observeEvent(input$toggleRawData, {
    shinyjs::toggle("rawDataContent")
    # Update button text to show appropriate arrow
    if (input$toggleRawData %% 2 == 1) {
      updateActionButton(session, "toggleRawData", "Raw Data ▲")
    } else {
      updateActionButton(session, "toggleRawData", "Raw Data ▼")
    }
  })

}

# Run the Shiny app
shinyApp(ui = ui, server = server)
