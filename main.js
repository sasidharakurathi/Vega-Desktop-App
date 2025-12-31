const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

const isDev = !app.isPackaged;

function createWindow() {
    const { width, height } = screen.getPrimaryDisplay().bounds;

    mainWindow = new BrowserWindow({
        width: width,
        height: height,
        x: 0,
        y: 0,
        frame: false, 
        transparent: true, 
        alwaysOnTop: false, 
        hasShadow: false, 
        resizable: true, 
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        autoHideMenuBar: true,
    });

    mainWindow.maximize(); 
    mainWindow.show();
    mainWindow.loadFile(path.join(__dirname, 'gui', 'index.html'));
    // mainWindow.webContents.openDevTools(); // Debug Console
}

function startPythonBackend() {
    let scriptPath;
    let pythonCmd;
    let args;

    if (isDev) {
        // DEVELOPMENT MODE: Run python script directly
        console.log("Running in DEV mode");
        pythonCmd = 'python';
        scriptPath = path.join(__dirname, 'backend', 'server.py');
        args = ['-u', scriptPath];
    } else {
        // PRODUCTION MODE: Run the compiled executable
        console.log("Running in PROD mode");
        // In prod, resources are moved to a special folder
        const backendPath = path.join(process.resourcesPath, 'backend', 'vega_engine', 'vega_engine.exe');
        pythonCmd = backendPath;
        args = []; // No args needed for exe
    }

    console.log(`Starting Backend: ${pythonCmd}`);
    
    // Spawn the process
    pythonProcess = spawn(pythonCmd, args);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[PY]: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[PY ERR]: ${data}`);
    });
}

app.whenReady().then(() => {
    startPythonBackend(); 
    setTimeout(createWindow, 1000); 
});



ipcMain.on('app-quit', () => {
    if (pythonProcess) pythonProcess.kill();
    app.quit();
});

ipcMain.on('app-minimize', () => {
    if (mainWindow) mainWindow.minimize();
});

ipcMain.on('app-maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});


ipcMain.on('app-compact-mode', (event, isCompact) => {
    if (!mainWindow) return;
    
    if (isCompact) {
        
        mainWindow.unmaximize();
        
        const { width } = screen.getPrimaryDisplay().workAreaSize;
        const newX = Math.floor((width / 2) - 60);
        
        mainWindow.setBounds({ x: newX, y: 20, width: 120, height: 120 });
        mainWindow.setAlwaysOnTop(true, 'screen-saver'); 
    } else {
        
        mainWindow.setAlwaysOnTop(false);
        mainWindow.maximize();
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});