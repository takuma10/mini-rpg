const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    title: 'Mini Dungeon RPG',
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: { nodeIntegration: false }
  });
  win.loadFile('index.html');
  win.setMenuBarVisibility(false);
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
