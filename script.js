function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').textContent = data.detailed_review;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
