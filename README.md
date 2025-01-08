---

# Weather Data Automation and Visualization

## Overview

This project automates the process of fetching weather and tide data, integrating it into databases, and visualizing it through an interactive web application. The entire pipeline, from data extraction to visualization, is fully automated and cloud-based. The configuration and orchestration of the various steps in the workflow are handled using a **YAML** configuration, which is interpreted by cloud computing services to ensure smooth execution.

## Components

1. **Weather and Tide Data Fetching (Web Scraping)**: This component fetches weather and tide data for various UK cities from BBC websites using web scraping techniques. The data, such as temperature, wind speed, and tide times, is extracted and then stored in a cloud-based Google Sheet.
   
2. **Data Integration into SQLite Database**: The weather data is integrated into an SQLite database hosted on a cloud storage service like Amazon S3 or Google Cloud Storage. The integration script checks for duplicate entries, processes the data, and loads it into the database.
   
3. **Data Migration from SQLite to PostgreSQL**: A migration script automatically migrates the weather data from an SQLite database to a PostgreSQL instance hosted on a cloud service like AWS RDS or Google Cloud SQL. This ensures that the data is available in a scalable relational database.

4. **Interactive Weather Visualization with R Shiny**: The R Shiny app fetches data from PostgreSQL and visualizes it in real-time, providing interactive plots and maps. The app is fully automated and hosted on cloud-based infrastructure, ensuring smooth access and visualization.

## Cloud Automation Process

### 1. **Data Extraction and Web Scraping (Automated with Cloud Functions)**
   - **How it Works**: A cloud-based function (such as **AWS Lambda**, **Google Cloud Functions**, or **Azure Functions**) is used to periodically trigger the script that scrapes weather and tide data from BBC websites.
   - **Automation**: The YAML configuration includes time-based triggers to automatically run the web scraping script at scheduled intervals (e.g., every hour or every day). After execution, the extracted data is uploaded to a **Google Sheet** using the **Google Sheets API**.
   - **Cloud Benefits**: The serverless nature of cloud functions ensures no server infrastructure management is required, and the scraping is done automatically at regular intervals.

### 2. **Data Integration into SQLite Database (ETL Pipeline on Cloud)**
   - **How it Works**: Once the data is stored in the Google Sheets, a cloud-based **ETL pipeline** (using **AWS Glue**, **Google Cloud Dataflow**, or **Azure Data Factory**) is set up to extract the data, transform it as needed (e.g., cleaning, checking for duplicates), and load it into an **SQLite database**.
   - **Automation**: The YAML configuration defines the ETL pipeline, ensuring data is processed automatically without any manual intervention. It includes error handling steps to catch potential issues such as missing or malformed data.
   - **Cloud Benefits**: Cloud platforms ensure the ETL process runs reliably at the scheduled times, and no resources are consumed unnecessarily when the script is not running.

### 3. **Data Migration from SQLite to PostgreSQL (Automated Data Migration)**
   - **How it Works**: A migration script runs in the cloud and automatically moves data from the **SQLite** database to a **PostgreSQL** instance hosted on cloud-based services like **AWS RDS** or **Google Cloud SQL**.
   - **Automation**: The YAML configuration specifies the time-based trigger or event-based trigger that kicks off the migration process. The script automatically handles data type conversions, missing values, and inserts them into PostgreSQL.
   - **Cloud Benefits**: Cloud computing services manage the databases, scaling them automatically based on usage and ensuring high availability during migration.

### 4. **Interactive Data Visualization with R Shiny (Automated Deployment on Cloud Infrastructure)**
   - **How it Works**: The **R Shiny** app fetches weather data from PostgreSQL and displays it through interactive plots and maps. The Shiny app is deployed on a cloud service like **AWS EC2**, **Google Cloud Compute Engine**, or **Azure Web Services**.
   - **Automation**: The YAML configuration orchestrates the deployment process of the Shiny app. The app is set up to scale automatically, handle incoming requests efficiently, and run continuously without manual intervention.
   - **Cloud Benefits**: Cloud services provide auto-scaling, ensuring that the Shiny app can handle varying amounts of user traffic. Continuous integration and deployment (CI/CD) pipelines are triggered to automatically update the app whenever new features or updates are deployed.

### 5. **End-to-End Data Pipeline with Cloud Monitoring and Logging**
   - **How it Works**: The entire process is monitored using cloud-based tools like **AWS CloudWatch**, **Google Cloud Logging**, or **Azure Monitor** to track the health and status of each task (data extraction, migration, and visualization).
   - **Automation**: The YAML configuration includes monitoring parameters that automatically trigger notifications if any step in the pipeline fails, ensuring issues are detected and addressed quickly.
   - **Cloud Benefits**: Cloud monitoring and logging services automatically record every action, providing real-time insights into the system's health. This allows for rapid troubleshooting and problem resolution without manual intervention.

### 6. **Cloud Storage and Database Management**
   - **How it Works**: All the data—raw and processed—is stored in **Google Sheets**, **SQLite**, and **PostgreSQL** databases, all hosted on cloud services.
   - **Automation**: Cloud-managed databases automatically handle scaling, backup, and fault tolerance, ensuring data is always accessible and secure. The YAML configuration defines how data should be managed, including where to store it and how to back it up.
   - **Cloud Benefits**: The cloud providers ensure automatic scaling, backups, and data durability, freeing up the user from worrying about infrastructure management.

## How YAML Configuration Works

The YAML configuration is integral to automating each step of this workflow. It defines:

- **Scheduled triggers** for each cloud service (e.g., web scraping script execution, ETL pipeline scheduling).
- **Configuration settings** for cloud functions, databases, and app deployment.
- **Scaling and monitoring parameters** for ensuring the system performs efficiently.
- **Cloud-based event triggers** that move the data from one stage to another (e.g., from Google Sheets to SQLite, from SQLite to PostgreSQL).

By using YAML, this project leverages cloud computing to automate the entire process, ensuring that data is consistently fetched, processed, stored, and visualized with minimal manual intervention.

## Conclusion

The entire project is automated using **cloud computing** and **YAML configuration** to handle the scheduling, execution, and orchestration of various components. The cloud-based infrastructure ensures scalability, fault tolerance, and continuous operation, with minimal maintenance required. All steps—from data extraction and migration to visualization—are fully automated, enabling real-time data analysis and seamless visualization of weather information.
