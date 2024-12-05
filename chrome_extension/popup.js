// popup.js

document.getElementById('fillForm').addEventListener('click', () => {
  // Update status
  const statusDiv = document.getElementById('status');
  statusDiv.textContent = 'Filling form...';

  // Query the active tab and send a message to content script
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
          statusDiv.textContent = 'No active tab found.';
          return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: "fillForm" }, (response) => {
          if (chrome.runtime.lastError) {
              statusDiv.textContent = 'Error: ' + chrome.runtime.lastError.message;
              return;
          }

          if (response && response.status) {
              statusDiv.textContent = response.status;
          } else {
              statusDiv.textContent = 'Unknown response from content script.';
          }
      });
  });
});
