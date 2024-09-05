const express = require('express');
const { initTracer, FORMAT_HTTP_HEADERS } = require('jaeger-client');
const https = require('https');

// Configure Jaeger Tracing
const config = {
  serviceName: 'jaeger-sample-service',
  reporter: {
    collectorEndpoint: 'http://localhost:14268/api/traces',
  },
  sampler: {
    type: 'const',
    param: 1,
  },
};

// Initialize Jaeger Tracer
const tracer = initTracer(config);

// Create an Express application
const app = express();
const port = 3000;

// Define a route
app.get('/', (req, res) => {
  const span = tracer.startSpan('http_request');

  // Perform the HTTPS GET request
  https.get('https://jsonplaceholder.typicode.com/users', response => {
    let data = [];
    const headerDate = response.headers && response.headers.date ? response.headers.date : 'no response date';
    console.log('Status Code:', response.statusCode);
    console.log('Date in Response header:', headerDate);

    response.on('data', chunk => {
      data.push(chunk);
    });

    response.on('end', () => {
      span.finish(); // Finish the span after the request completes

      console.log('Response ended: ');
      const users = JSON.parse(Buffer.concat(data).toString());

      let result = '';
      for (let user of users) {
        result += `Got user with id: ${user.id}, name: ${user.name}\n`;
      }

      // Send the response to the client
      res.send(result);
    });
  }).on('error', err => {
    span.finish(); // Finish the span even in case of error
    console.log('Error: ', err.message);
    res.status(500).send('Error occurred');
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
