const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 4000;

// Middleware to enable CORS
app.use(cors());

// Define the path to the deviceId.json file
const DEVICE_ID_PATH = path.join('C:', 'Users', 'user', 'Desktop', 'deviceId.json');
// const DEVICE_ID_PATH = path.join('F:', 'deviceId.json');

// Endpoint to check for the deviceId file
app.get('/check-device', (req, res) => {
  if (fs.existsSync(DEVICE_ID_PATH)) {
    const deviceId = JSON.parse(fs.readFileSync(DEVICE_ID_PATH, 'utf8')).adminDeviceId;
    res.json({ success: true, deviceId });
  } else {
    res.json({ success: false });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`File checker server is running on http://localhost:${PORT}`);
});
