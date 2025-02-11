FROM rocker/shiny:latest

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libpng-dev \
    libudunits2-dev \
    libgdal-dev \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e 'install.packages(c(\
    "remotes", \
    "rsconnect", \
    "DBI", \
    "dplyr", \
    "leaflet", \
    "lubridate", \
    "plotly", \
    "RPostgres", \
    "RSQLite", \
    "shinyjs" \
    ), repos="https://cran.rstudio.com")'

    
RUN R -e 'if ("terra" %in% installed.packages()) remove.packages("terra")'

    

# Copy only app.r
COPY app.r /srv/shiny-server/
WORKDIR /srv/shiny-server

# Create directory for mounted data
RUN mkdir -p /srv/shiny-server/data

EXPOSE 3838
