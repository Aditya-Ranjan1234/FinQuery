// vercel-build.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Starting Vercel build process...');

// Ensure required directories exist
const dirs = [
  'hackrx_llm/static',
  'hackrx_llm/templates',
  'documents',
  'backend_index'
];

dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    console.log(`Creating directory: ${dir}`);
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Install Python dependencies
try {
  console.log('Installing Python dependencies...');
  execSync('pip install -r requirements-vercel.txt', { stdio: 'inherit' });
  
  // Verify Python installation
  const pythonVersion = execSync('python --version').toString();
  console.log(`Using Python: ${pythonVersion}`);
  
  // Verify pip installation
  const pipPackages = execSync('pip list').toString();
  console.log('Installed Python packages:', pipPackages);
  
  console.log('Build completed successfully');
} catch (error) {
  console.error('Build failed:');
  console.error(error.stdout?.toString() || error.message);
  process.exit(1);
}
