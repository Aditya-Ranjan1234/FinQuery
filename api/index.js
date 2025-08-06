const { createServer } = require('@vercel/node');
const { spawn } = require('child_process');
const path = require('path');

module.exports = async (req, res) => {
  try {
    // Forward the request to the Python webhook
    const pythonProcess = spawn('python', [
      '-m', 'hackrx_llm.webhook',
      '--serverless'
    ], {
      env: {
        ...process.env,
        VERCEL: '1',
        PYTHONUNBUFFERED: '1',
        PYTHONPATH: process.cwd()
      }
    });

    let responseData = '';
    pythonProcess.stdout.on('data', (data) => {
      responseData += data.toString();
    });

    let errorData = '';
    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      console.error(`Python error: ${data}`);
    });

    // Send request data to Python process
    if (req.method === 'POST') {
      pythonProcess.stdin.write(JSON.stringify(req.body));
    } else if (req.method === 'GET' && req.url === '/health') {
      pythonProcess.stdin.write(JSON.stringify({ path: '/health' }));
    }
    pythonProcess.stdin.end();

    // Wait for the process to exit
    const exitCode = await new Promise((resolve) => {
      pythonProcess.on('close', resolve);
    });

    if (exitCode !== 0) {
      console.error(`Python process exited with code ${exitCode}`);
      if (errorData) console.error('Python error output:', errorData);
      return res.status(500).json({ 
        error: 'Internal server error',
        details: errorData || 'Python process failed'
      });
    }

    try {
      const response = responseData ? JSON.parse(responseData) : {};
      return res.status(200).json(response);
    } catch (e) {
      console.error('Failed to parse Python response:', e);
      return res.status(500).json({ 
        error: 'Invalid response from server',
        details: responseData
      });
    }
  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({ 
      error: 'Server error',
      details: error.message 
    });
  }
};
