<?php
// Retrieve data from the GET request
$temperature = isset($_GET['temperature']) ? $_GET['temperature'] : null;
$humidity = isset($_GET['humidity']) ? $_GET['humidity'] : null;

// Check if both temperature and humidity are present before proceeding
// Print received temperature and humidity for debugging
echo "Received Temperature: " . $temperature . "\n";
echo "Received Humidity: " . $humidity . "\n";

if ($temperature !== null && $humidity !== null) {
    // Your database connection code goes here

    // Example: Insert data into a MySQL database
    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "weather";

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Insert data into the database
    $sql = "INSERT INTO data(temperature, humidity) VALUES ('$temperature', '$humidity')";

    if ($conn->query($sql) === TRUE) {
        echo "Insertion Success";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
    
    // Close the database connection 
     $conn->close();
} else {
    // If either temperature or humidity is missing in the request
    echo "Error: Temperature or humidity missing in the request.";
}
?>
