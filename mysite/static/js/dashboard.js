document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dashboardForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        fetch('/dashboard/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                'category': document.getElementById('category').value,
                'item': document.getElementById('item').value,
                'fromDate': document.getElementById('fromDate').value,
                'toDate': document.getElementById('toDate').value
            })
        }).then(response => response.json()).then(data => {
            // Update table and chart with new data.
        }).catch(error => console.error('Error:', error));
    });
});
