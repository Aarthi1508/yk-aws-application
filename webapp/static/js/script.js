$(document).ready(function () {

    $('#generateShadowMatrix').click(function () {
        $('#loader').show(); // Show the loader icon
        var formData = $('#timestampForm').serialize();
    
        $.ajax({
            type: 'POST',
            url: '/shadow-analysis/', // URL to your view function
            data: formData,
            success: function (response) {
                $('#loader').hide(); // Hide the loader icon
                $('#shadowMatrixResult').text(response.message); // Assuming your view returns a JSON object with a 'message' field
                alert('Shadow matrix is pushed to MongoDB');
    
                // Remove any existing viewResultsButton
                $('#viewResultsButton').remove();
    
                // Create a button to view the results
                var viewResultsButton = $('<button>').text('View Results').attr('id', 'viewResultsButton');
                $('#buttonContainer').append(viewResultsButton);
    
                // Add click event handler for the viewResultsButton
                $('#viewResultsButton').click(function () {
                    // Redirect to the page where you display the results
                    window.location.href = '/visualize-shadow-matrix/';
                });
            },
            error: function (error) {
                $('#loader').hide(); // Hide the loader icon
                $('#shadowMatrixResult').text(''); // Clear the result div
                alert('Error: Something went wrong!');
                console.log(error);
            }
        });
    });
    

    $('#superimposeShadowMatrix').click(function () {
        console.log("Superimpose button is clicked")
        $('#loader').show(); // Show the loader icon
        $.ajax({
            type: 'GET',
            url: '/superimpose-shadow-matrix/', // URL to your view function
            success: function (response) {
                $('#loader').hide(); // Hide the loader icon
                // Update page content with the new information
                // For example, you can update an image or display a message
                console.log('Shadow matrix superimposed successfully!');
                // Add code here to update the page content
                window.location.href = '/superimpose-shadow-matrix/';
            },
            error: function (error) {
                $('#loader').hide(); // Hide the loader icon
                alert('Error: Something went wrong!');
                console.log(error);
            }
        });
    });
    
    
});
