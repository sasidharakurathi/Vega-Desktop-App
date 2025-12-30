const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("vega", {
  shutdown: () => ipcRenderer.send("shutdown")
});
