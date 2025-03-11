document.addEventListener('DOMContentLoaded', function() {
    // Load available videos when the page loads
    loadVideos();
    
    // Set up form submission handlers
    setupFormHandlers();
});

function loadVideos() {
    // Get the video select dropdown
    const videoSelect = document.getElementById('youtube_id');
    if (!videoSelect) return;
    
    // Fetch the list of available videos
    fetch('/videos')
        .then(response => response.json())
        .then(videos => {
            // Clear existing options
            videoSelect.innerHTML = '<option value="">Select a video</option>';
            
            // Add options for each video
            videos.forEach(videoId => {
                const option = document.createElement('option');
                option.value = videoId;
                option.textContent = videoId;
                videoSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading videos:', error));
}

function setupFormHandlers() {
    // Download form handler
    const downloadForm = document.getElementById('downloadForm');
    if (downloadForm) {
        downloadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(downloadForm);
            const resultsDiv = document.getElementById('results');
            const resultsContent = document.getElementById('resultsContent');
            
            // Show loading state
            resultsDiv.style.display = 'block';
            resultsContent.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p>Downloading comments...</p></div>';
            
            // Submit the form via AJAX
            fetch('/download', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                let html = '<h4>Download Results:</h4><ul>';
                
                for (const [videoId, result] of Object.entries(data)) {
                    const status = result.success ? 'success' : 'danger';
                    html += `<li class="text-${status}">${videoId}: ${result.message}</li>`;
                }
                
                html += '</ul>';
                
                if (Object.values(data).some(result => result.success)) {
                    html += '<p>Refresh the page to see newly downloaded videos in the dropdown.</p>';
                }
                
                resultsContent.innerHTML = html;
                
                // Reload the video list
                loadVideos();
            })
            .catch(error => {
                resultsContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            });
        });
    }
    
    // Persona generation form handler
    const personaForm = document.getElementById('personaForm');
    if (personaForm) {
        personaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(personaForm);
            const resultsDiv = document.getElementById('results');
            const resultsContent = document.getElementById('resultsContent');
            
            // Show loading state
            resultsDiv.style.display = 'block';
            resultsContent.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p>Generating personas...</p></div>';
            
            // Submit the form via AJAX
            fetch('/generate_personas', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const videoId = formData.get('youtube_id');
                    resultsContent.innerHTML = `
                        <div class="alert alert-success">Personas generated successfully!</div>
                        <a href="/view_personas/${videoId}" class="btn btn-primary">View Personas</a>
                    `;
                } else {
                    resultsContent.innerHTML = `<div class="alert alert-danger">Error: ${data.message}</div>`;
                }
            })
            .catch(error => {
                resultsContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            });
        });
    }
}
