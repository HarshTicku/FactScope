// Initialize context menu items
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "factscope",
      title: "Analyze with FactScope",
      contexts: ["selection"]
    });
    
    chrome.contextMenus.create({
      id: "factscope-summarize",
      parentId: "factscope",
      title: "Summarize",
      contexts: ["selection"]
    });
    
    chrome.contextMenus.create({
      id: "factscope-factcheck",
      parentId: "factscope",
      title: "Fact Check",
      contexts: ["selection"]
    });
    
    chrome.contextMenus.create({
      id: "factscope-bias",
      parentId: "factscope",
      title: "Detect Bias",
      contexts: ["selection"]
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId.startsWith('factscope-')) {
      const action = info.menuItemId.replace('factscope-', '');
      const selectedText = info.selectionText;
      
      // Get API endpoint from settings
      chrome.storage.sync.get(['apiEndpoint'], (settings) => {
        const apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';
        
        // Send message to content script to show inline results
        chrome.tabs.sendMessage(tab.id, {
          action: 'showInlineResults',
          analysisType: action,
          text: selectedText,
          apiEndpoint: apiEndpoint
        });
      });
    }
});

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener((command, tab) => {
    if (command === 'quick_summary') {
      // Execute content script to get selected text and perform quick summary
      chrome.tabs.sendMessage(tab.id, { action: 'getSelectedText' }, (response) => {
        if (response && response.selectedText) {
          chrome.storage.sync.get(['apiEndpoint'], (settings) => {
            const apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';
            
            // Send to API
            fetch(`${apiEndpoint}/summarize`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: response.selectedText })
            })
            .then(res => res.json())
            .then(data => {
              // Send result back to content script to display
              chrome.tabs.sendMessage(tab.id, {
                action: 'showQuickSummary',
                result: data
              });
            })
            .catch(error => {
              console.error('Error with quick summary:', error);
              chrome.tabs.sendMessage(tab.id, {
                action: 'showError',
                message: 'Unable to get summary. Please try again.'
              });
            });
          });
        }
      });
    }
});

// Handle installation and updates
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
      // First time installation
      chrome.tabs.create({ url: 'onboarding.html' });
    } else if (details.reason === 'update') {
      // Show update notification
      const previousVersion = details.previousVersion;
      const currentVersion = chrome.runtime.getManifest().version;
      
      if (previousVersion !== currentVersion) {
        // Only show for major or minor updates
        const prevParts = previousVersion.split('.');
        const currentParts = currentVersion.split('.');
        
        if (prevParts[0] !== currentParts[0] || prevParts[1] !== currentParts[1]) {
          chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'FactScope Updated',
            message: `Updated to version ${currentVersion} with new features and improvements.`,
            buttons: [{ title: 'See What\'s New' }]
          });
        }
      }
    }
});

// Handle notification clicks
chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
    if (buttonIndex === 0) {
      chrome.tabs.create({ url: 'whatsnew.html' });
    }
});
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "open-factscope",
      title: "Open FactScope",
      contexts: ["all"]
    });
});
  
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "open-factscope") {
      chrome.windows.create({
        url: 'popup.html',
        type: 'popup',
        width: 800,
        height: 800
      });
    }
});