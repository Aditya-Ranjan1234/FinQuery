#!/usr/bin/env node

/**
 * Vercel Build Script for FinQuery Application
 * 
 * This script handles the build process on Vercel, including:
 * - Installing Python dependencies
 * - Setting up environment variables
 * - Building any necessary assets
 * - Verifying the installation
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const PYTHON = process.env.PYTHON || 'python3';
const PIP = process.env.PIP || 'pip3';
const PROJECT_ROOT = __dirname;
const REQUIREMENTS_FILE = path.join(PROJECT_ROOT, 'requirements-vercel.txt');
const PYTHON_PATHS = [
  '/usr/local/bin/python3',
  '/usr/bin/python3',
  'python3',
  'python'
];

// Utility functions
function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
  
  // Write to both console and a log file
  console.log(logMessage);
  
  try {
    fs.appendFileSync('vercel-build.log', logMessage + '\n');
  } catch (e) {
    console.error(`Failed to write to log file: ${e.message}`);
  }
}

function runCommand(command, cwd = PROJECT_ROOT) {
  log(`Running: ${command}`);
  try {
    const output = execSync(command, { 
      cwd, 
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      encoding: 'utf-8'
    });
    
    if (output) {
      log(`Output: ${output}`);
    }
    
    return { success: true, output };
  } catch (error) {
    const errorMessage = `Command failed: ${command}\n${error.message}\n${error.stderr || ''}`;
    log(errorMessage, 'error');
    return { success: false, error: new Error(errorMessage) };
  }
}

// Main build function
async function main() {
  log('Starting Vercel build process for FinQuery');
  
  // Ensure Python is available
  log('Checking for Python installation...');
  let pythonPath = '';
  
  for (const py of PYTHON_PATHS) {
    const { success } = runCommand(`${py} --version`);
    if (success) {
      pythonPath = py;
      break;
    }
  }
  
  if (!pythonPath) {
    log('Python not found. Please ensure Python 3.8+ is installed.', 'error');
    process.exit(1);
  }
  
  log(`Using Python: ${pythonPath}`);
  
  // Install Python dependencies
  log('Installing Python dependencies...');
  
  // First upgrade pip
  const pipUpgradeResult = runCommand(`${pythonPath} -m pip install --upgrade pip`);
  if (!pipUpgradeResult.success) {
    log('Failed to upgrade pip', 'error');
    process.exit(1);
  }
  
  // Install requirements
  const installResult = runCommand(`${pythonPath} -m pip install -r ${REQUIREMENTS_FILE}`);
  if (!installResult.success) {
    log('Failed to install Python dependencies', 'error');
    process.exit(1);
  }
  
  // Create necessary directories
  log('Creating required directories...');
  const dirsToCreate = [
    'hackrx_llm/static',
    'hackrx_llm/templates',
    'documents',
    'backend_index'
  ];
  
  dirsToCreate.forEach(dir => {
    const dirPath = path.join(PROJECT_ROOT, dir);
    try {
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
        log(`Created directory: ${dirPath}`);
      }
    } catch (error) {
      log(`Failed to create directory ${dirPath}: ${error.message}`, 'error');
      process.exit(1);
    }
  });
  
  // Verify the installation
  log('Verifying installation...');
  const verifyResult = runCommand(`${pythonPath} -c "import flask, sys; print(f'Python {sys.version}\nFlask {flask.__version__}')"`);
  
  if (!verifyResult.success) {
    log('Verification failed', 'error');
    process.exit(1);
  }
  
  // List installed packages for debugging
  log('Installed Python packages:');
  runCommand(`${pythonPath} -m pip list`);
  
  log('Build completed successfully!', 'success');
}

// Run the build
main().catch(error => {
  log(`Build failed: ${error.message}`, 'error');
  process.exit(1);
});
