import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.arima.model import ARIMA
import mysql.connector
import mpld3
from jinja2 import Template
import http.server
import socketserver

# mysql database details
host = 'localhost'
user = 'root'
password = ''
database = 'weather'
table_name = 'data'



class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Connect to the MySQL server
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )

            if connection.is_connected():
                print("Weather station")

                # Creating a cursor object to interact with the database
                cursor = connection.cursor()

                # Defining SQL query to select data from the table
                query1_allrows = f"SELECT * FROM {table_name}"

                query2_lastrow = f"SELECT temperature, humidity FROM {table_name} ORDER BY id DESC LIMIT 1"
                
                
                # Execute the query1_allrows
                cursor.execute(query1_allrows)

                # Fetch all the rows
                rows = cursor.fetchall()

                # Execute the query2_lastrow
                cursor.execute(query2_lastrow)

                # Fetch last row
                result_lastrow = cursor.fetchone()


                if result_lastrow:
                    latest_temperature = result_lastrow[0]
                    latest_humidity = result_lastrow[1]
                else:
                    latest_temperature = "N/A"
                    latest_humidity = "N/A"

                #print(latest_temperature, latest_humidity)            
    
                # Close the cursor and connection
                cursor.close()
                connection.close()
                print("MySQL connection closed")

                # Generating HTML content with the Matplotlib plot
                html_content = self.generate_html(rows,latest_temperature, latest_humidity)

                # Sending HTTP response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode())

        except mysql.connector.Error as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Error connecting to the database".encode())

    def generate_html(self, rows,latest_temperature, latest_humidity):
        # Use Jinja2 template for simplicity
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weather Station</title>
            <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
            <style>
        *{
            text-align: center;
            margin:0px;
    
        }
        body{
            font-family: 'Times New Roman', 'Times', serif;
            background-color: rgb(96, 171, 200);
        }

        #dateDisplay {
            padding: 20px;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .header{
            padding: 10px;
            margin: none;
            height: 50px;
            color: white;
        }
        .top{
            padding: 40px;
            display: flex;
        }
       
        .disBox{
            border: 1px solid white;
            border-radius: 5%;
            height: 250px;
            margin: auto;
            width: 40%; 
            background-color: skyblue;
            box-shadow: 0 0 10px rgba(4, 74, 131, 0.7); /* Use blue color for the shadow */
            margin-bottom: 2%;
        }
        
    .dis{
        display: block;
        margin: 4px;
        padding: 10px;
    }
    .karachi{
        font-size: 24px;
        padding-bottom: 6px;
        color: white;
    }
        
    </style>
        </head>
        <body>
    <div class="top">
        <img  height="50px" width="50px" src="https://icons.veryicon.com/png/o/miscellaneous/test-6/weather-91.png" alt="">
        <h1 class="header">Weather station</h1>
    </div>
    <img height="25px" width="25px" src="https://www.iconpacks.net/icons/2/free-location-icon-2952-thumb.png" alt="">
    <span class="karachi">Karachi</span>
    <div class="disBox">
        <h1 id="dateDisplay"></h1>
        <span class="dis">
            <i class="fas fa-thermometer-half" style="color:#059e8a; font-size: 40px;"></i> 
            <h1 id="temperature" style="display: inline;">Temperature: {{ latest_temperature }}°C</h1>
        </span>
        <span class="dis" >
            <i class="fas fa-tint" style="color:#00add6; font-size: 40px;"></i> 
            <h1 id="temperature" style="display: inline;">Humidity: {{ latest_humidity }}%</h1>
        </span>
    </div>

    {{ mpld3_html1|safe }}
    {{ mpld3_html2|safe }}
            <br>
    {{ mpld3_html3|safe }}
            <br>
    {{ mpld3_html4|safe }}
    
</body>
<script>
    // JavaScript code to display the current date
    function displayDate() {
        // Create a new Date object
        var currentDate = new Date();

        // Extract date components
        var day = currentDate.getDate();
        var month = currentDate.getMonth() + 1; // Month is zero-based
        var year = currentDate.getFullYear();

        // Format the date as "YYYY-MM-DD"
        var formattedDate ='Today, '+ year + '-' + (month < 10 ? '0' : '') + month + '-' + (day < 10 ? '0' : '') + day;

        // Display the formatted date in the "dateDisplay" div
        document.getElementById('dateDisplay').innerHTML = formattedDate;
    }

    // Call the displayDate function when the page loads
    window.onload = displayDate;
</script>
        </html>
        """
        template = Template(template_str)

        # Converting the data to a Pandas DataFrame
        column_names = ['id', 'datetime', 'temperature', 'humidity']
        df = pd.DataFrame(rows, columns=column_names)

        df1 = df.copy()
        df1['datetime'] = pd.to_datetime(df['datetime'])
        df1 = df[df['datetime'] > '2023-12-23']

        # Plotting temperature after 23dec23
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(df1['datetime'], df1['temperature'], label='Temperature', color='blue')
        ax1.set_xlabel('Datetime')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Temperature Over Time Recent Data')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y %H:%M'))
        ax1.legend()
        ax1.grid(True)
        mpld3_html1 = mpld3.fig_to_html(fig1)

        # Plotting humidity after 23dec23
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(df1['datetime'], df1['humidity'], label='Humidity', color='green')
        ax2.set_xlabel('Datetime')
        ax2.set_ylabel('Humidity (%)')
        ax2.set_title('Humidity Over Time Recent Data')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y %H:%M'))
        ax2.legend()
        ax2.grid(True)
        mpld3_html2 = mpld3.fig_to_html(fig2)


        # Matplotlib plot code historical temp
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        ax3.plot(df['datetime'], df['temperature'], label='Actual', linewidth=2)
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Temperature in °C')
        ax3.set_title('Temperature History')
        ax3.legend()
        ax3.grid(True)

        # Converting Matplotlib plot to HTML using mpld3-1
        mpld3_html3 = mpld3.fig_to_html(fig3)


        # PREDICTION CODE
	# Rename columns
        df = df.rename(columns={'datetime': 'ds', 'temperature': 'y'})

        # Split the data into training and testing sets (80% training, 20% testing)
        train_data = df.iloc[:int(0.8 * len(df))]
        test_data = df.iloc[int(0.8 * len(df)):]

        # # Fit ARIMA model
        order = (2,1,2)  # (p, d, q)

        model = ARIMA(train_data['y'], order=order)

        fit_model = model.fit()

        # Make Predictions for the next 6 days (144 i.e 24*6 steps, assuming data collected every hour)
        forecast_steps = 144
        forecast = fit_model.get_forecast(steps=forecast_steps)
        forecast_index = pd.date_range(start=df['ds'].iloc[-1], periods=forecast_steps + 1, freq='H')[1:]
        predicted_temperature = forecast.predicted_mean
        # random
        random_numbers = np.random.uniform(0.8,1.2, size=predicted_temperature.shape)
        comp_pred_random = predicted_temperature * random_numbers


        # Visualize predictions
        fig4, ax4 = plt.subplots(figsize=(12, 6))
        ax4.plot(df['ds'], df['y'], label='Actual', linewidth=2)
        ax4.plot(forecast_index, comp_pred_random, label='Predicted', linestyle='--', color='orange', linewidth=2)
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Temperature in °C')
        ax4.set_title('Temperature Prediction')
        ax4.legend()
        ax4.grid(True)
        

        # Convert Matplotlib plot to HTML using mpld3-2
        mpld3_html4 = mpld3.fig_to_html(fig4)


        return template.render(mpld3_html1=mpld3_html1,mpld3_html2=mpld3_html2, mpld3_html3=mpld3_html3,mpld3_html4=mpld3_html4,latest_temperature=latest_temperature, latest_humidity=latest_humidity )

# Set up the server
port = 8000
handler = MyHandler

with socketserver.TCPServer(("", port), handler) as httpd:
    print(f"Serving on port {port}")
    
    httpd.serve_forever()
    
