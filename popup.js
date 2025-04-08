document.addEventListener('DOMContentLoaded', () => {
  // Populate datalist with "Current Page" URL.
  chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
    const inputBar = document.getElementById('input-bar');
    inputBar.value = ''; // Clear input to show placeholder.
    const dataList = document.getElementById('urlSuggestions');
    dataList.innerHTML = `<option value="${tab.url}" label="Current Page"></option>`;
  });

  // Add an event listener for when the user leaves the input field.
  const inputBar = document.getElementById('input-bar');
  inputBar.addEventListener('change', () => {
    // Start verification when input changes.
    verifyContent(inputBar.value);
  });
});

// Function to send a POST request to your backend.
function verifyContent(textOrUrl) {
  const apiKey = "your_api_key_here";
  const endpoint = "http://localhost:8000/evaluate";

  fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: textOrUrl,
      api_key: apiKey
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log("Evaluation Result:", data);
    // "final_credibility_score" is a float between 0 and 1.
    const trustPercent = data.final_credibility_score * 100;
    animateTrustMeter(trustPercent);
    updateCredibilityStatus(data.final_credibility_score > 0.5);
    document.getElementById('summary-text').textContent = data.summary || "Summary not available.";
    
    // If you want a "consensus summary"
    document.getElementById('consensus-summary').textContent = data.consensus_summary || "Not available.";
    
    // ... etc ...
  })
  .catch(error => {
    console.error("Error verifying content:", error);
  });
}

function animateTrustMeter(finalScore) {
  let currentScore = 0;
  const duration = 1000; // 1 second animation.
  const stepTime = 20;
  const steps = duration / stepTime;
  const increment = finalScore / steps;
  const interval = setInterval(() => {
    currentScore += increment;
    if (currentScore >= finalScore) {
      currentScore = finalScore;
      clearInterval(interval);
      if (finalScore > 70) {
        triggerThumbAnimation('up');
      } else if (finalScore < 50) {
        triggerThumbAnimation('down');
      }
    }
    document.getElementById('trust-score').textContent = Math.floor(currentScore) + '%';
    document.getElementById('trust-fill').style.width = Math.floor(currentScore) + '%';
  }, stepTime);
}

function triggerThumbAnimation(direction) {
  const duration = 500;
  if (direction === 'up') {
    const thumbUp = document.getElementById('thumb-up');
    thumbUp.classList.add('shake');
    setTimeout(() => {
      thumbUp.classList.remove('shake');
      thumbUp.classList.add('enlarged');
    }, duration);
  } else if (direction === 'down') {
    const thumbDown = document.getElementById('thumb-down');
    thumbDown.classList.add('shake');
    setTimeout(() => {
      thumbDown.classList.remove('shake');
      thumbDown.classList.add('enlarged');
    }, duration);
  }
}

function updateCredibilityStatus(isCredible) {
  const status = document.getElementById('credibility-status');
  status.textContent = isCredible ? '✅ Credible Source' : '⚠️ Source Not Credible';
  status.style.color = isCredible ? '#4caf50' : '#f44336';
}

function displayRelatedArticles(articles) {
  const list = document.getElementById('related-articles');
  list.innerHTML = '';
  articles.forEach(article => {
    const li = document.createElement('li');
    li.innerHTML = `<a href="${article.url}" target="_blank">${article.title}</a>`;
    list.appendChild(li);
  });
}