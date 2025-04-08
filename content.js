// Display analysis results based on type
function displayAnalysisResults(container, result, type) {
    // Clear loading state
    container.innerHTML = '';
    
    switch (type) {
      case 'summarize':
        container.innerHTML = `
          <h3 style="margin-top: 0; margin-bottom: 12px; color: #333;">Summary</h3>
          <p style="line-height: 1.5; margin-bottom: 16px;">${result.summary || 'No summary available'}</p>
          ${result.keyPoints && result.keyPoints.length > 0 ? `
            <h3 style="margin: 0 0 8px; color: #333;">Key Points</h3>
            <ul style="padding-left: 20px; margin-top: 0;">
              ${result.keyPoints.map(point => `<li style="margin-bottom: 6px;">${point}</li>`).join('')}
            </ul>
          ` : ''}
        `;
        break;
        
      case 'factcheck':
        container.innerHTML = `
          <div style="text-align: center; margin-bottom: 16px;">
            <div style="font-size: 24px; font-weight: bold; color: ${getScoreColor(result.overallScore)};">
              ${result.overallScore}% Accurate
            </div>
          </div>
          
          ${result.claims && result.claims.length > 0 ? `
            <h3 style="margin: 0 0 12px; color: #333;">Claims Analyzed</h3>
            <div>
              ${result.claims.map(claim => `
                <div style="margin-bottom: 16px; padding: 10px; background: #f5f5f5; border-radius: 6px;">
                  <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-weight: 600;">${claim.text}</div>
                    <div style="font-weight: 600; color: ${getScoreColor(claim.score)};">${claim.verdict}</div>
                  </div>
                  <div style="margin-bottom: 8px;">
                    <div style="height: 6px; background: #eee; border-radius: 3px; overflow: hidden;">
                      <div style="height: 100%; width: ${claim.score}%; background: ${getScoreColor(claim.score)};"></div>
                    </div>
                  </div>
                  ${claim.explanation ? `<div style="font-size: 14px;">${claim.explanation}</div>` : ''}
                  ${claim.sources && claim.sources.length > 0 ? `
                    <div style="margin-top: 8px; font-size: 13px;">
                      <div style="font-weight: 600; margin-bottom: 4px;">Sources:</div>
                      <ul style="margin: 0; padding-left: 16px;">
                        ${claim.sources.map(source => `
                          <li><a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.title}</a></li>
                        `).join('')}
                      </ul>
                    </div>
                  ` : ''}
                </div>
              `).join('')}
            </div>
          ` : '<div>No claims were identified for analysis.</div>'}
        `;
        break;
        
      case 'sentiment':
        container.innerHTML = `
          <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 18px; margin-bottom: 8px;">Overall Sentiment</div>
            <div style="font-size: 24px; font-weight: bold; color: ${getSentimentColor(result.sentiment)};">
              ${getSentimentLabel(result.sentiment)}
            </div>
          </div>
          
          <div style="margin-bottom: 16px;">
            <div style="margin-bottom: 8px; font-weight: 600;">Sentiment Breakdown</div>
            <div style="display: flex; height: 24px; border-radius: 4px; overflow: hidden;">
              <div style="background-color: #e57373; width: ${result.negative}%;"></div>
              <div style="background-color: #fff176; width: ${result.neutral}%;"></div>
              <div style="background-color: #81c784; width: ${result.positive}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
              <div>Negative (${result.negative}%)</div>
              <div>Neutral (${result.neutral}%)</div>
              <div>Positive (${result.positive}%)</div>
            </div>
          </div>
          
          ${result.keyPhrases && result.keyPhrases.length > 0 ? `
            <div>
              <div style="font-weight: 600; margin-bottom: 8px;">Key Phrases</div>
              <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${result.keyPhrases.map(phrase => `
                  <span style="background: #f0f0f0; padding: 6px 10px; border-radius: 16px; font-size: 13px;">
                    ${phrase}
                  </span>
                `).join('')}
              </div>
            </div>
          ` : ''}
        `;
        break;
        
      default:
        container.innerHTML = `<div>Unknown analysis type: ${type}</div>`;
    }
}
  
// Helper functions for color-coding results
function getScoreColor(score) {
    if (score >= 80) return '#4caf50'; // Green
    if (score >= 60) return '#8bc34a'; // Light Green
    if (score >= 40) return '#ffc107'; // Amber
    if (score >= 20) return '#ff9800'; // Orange
    return '#f44336'; // Red
}
  
function getSentimentColor(sentiment) {
    if (sentiment >= 0.5) return '#4caf50'; // Positive - Green
    if (sentiment >= 0) return '#8bc34a';   // Slightly positive - Light Green
    if (sentiment >= -0.5) return '#ff9800'; // Slightly negative - Orange
    return '#f44336'; // Negative - Red
}
  
function getSentimentLabel(sentiment) {
    if (sentiment >= 0.5) return 'Very Positive';
    if (sentiment >= 0.1) return 'Positive';
    if (sentiment >= -0.1) return 'Neutral';
    if (sentiment >= -0.5) return 'Negative';
    return 'Very Negative';
}
  
// Show quick summary popup at mouse position
function showQuickSummary(result) {
    // Remove any existing quick summary
    const existingSummary = document.querySelector('.factscope-quick-summary');
    if (existingSummary) {
      existingSummary.remove();
    }
    
    // Create summary popup
    const summary = document.createElement('div');
    summary.className = 'factscope-quick-summary';
    
    // Get mouse position from last selection
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    // Position popup
    summary.style.left = `${rect.left + window.scrollX}px`;
    summary.style.top = `${rect.bottom + window.scrollY + 10}px`;
    
    // Add content
    summary.innerHTML = `
      <div class="factscope-quick-summary-header">
        <div class="factscope-quick-summary-title">
          <i>✓</i> FactScope Quick Check
        </div>
        <button class="factscope-quick-summary-close">✕</button>
      </div>
      <div>${result.summary || 'No information available for this selection.'}</div>
    `;
    
    // Add to page
    document.body.appendChild(summary);
    
    // Add close handler
    summary.querySelector('.factscope-quick-summary-close').addEventListener('click', () => {
      summary.remove();
    });
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (document.body.contains(summary)) {
        summary.remove();
      }
    }, 10000);
}
  
// Show error message
function showError(message) {
    // Remove any existing results
    removeExistingResults();
    
    // Create error container
    const container = document.createElement('div');
    container.className = 'factscope-inline-results';
    
    // Add error content
    container.innerHTML = `
      <div class="factscope-header">
        <div class="factscope-header-title">
          <span class="factscope-logo">✓</span>
          <span>FactScope Error</span>
        </div>
        <button class="factscope-close">✕</button>
      </div>
      <div class="factscope-content">
        <div class="factscope-error">${message}</div>
        <div>Please try again or check the extension settings.</div>
      </div>
    `;
    
    // Add to page
    document.body.appendChild(container);
    
    // Add close button handler
    container.querySelector('.factscope-close').addEventListener('click', () => {
      container.remove();
    });
    
    // Make the container draggable
    makeDraggable(container, container.querySelector('.factscope-header'));
}
  
// Helper to remove existing results
function removeExistingResults() {
    const existingResults = document.querySelector('.factscope-inline-results');
    if (existingResults) {
      existingResults.remove();
    }
}
  
// Make an element draggable
function makeDraggable(element, handle) {
    let offsetX, offsetY, isDragging = false;
    
    handle.addEventListener('mousedown', (e) => {
      isDragging = true;
      offsetX = e.clientX - element.getBoundingClientRect().left;
      offsetY = e.clientY - element.getBoundingClientRect().top;
      
      // Prevent text selection during drag
      e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const x = e.clientX - offsetX;
      const y = e.clientY - offsetY;
      
      // Set limits to keep within viewport
      const maxX = window.innerWidth - element.offsetWidth;
      const maxY = window.innerHeight - element.offsetHeight;
      
      element.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
      element.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
      
      // Switch from fixed to absolute positioning when dragging starts
      if (element.style.position !== 'absolute') {
        element.style.position = 'absolute';
      }
    });
    
    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
}

// Listen for messages (e.g., for quick summary)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "quickSummary" && message.selectedText) {
      fetch("http://localhost:8000/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: message.selectedText,
          api_key: "your_api_key_here"
        })
      })
      .then(response => response.json())
      .then(data => {
        alert("Summary: " + (data.summary || "Not available."));
      })
      .catch(error => console.error("Error in quick summary:", error));
    }
});