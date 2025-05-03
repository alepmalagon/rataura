// Main JavaScript for EVE Wiggin web frontend

$(document).ready(function() {
    // Show system search after first analysis
    let hasAnalyzed = false;
    
    // Handle analyze button click
    $('#analyze-btn').click(function() {
        // Show loading indicator
        $('#loading').show();
        $('#results').empty();
        $('#error-container').hide();
        
        // Get selected warzone and sort options
        const warzone = $('#warzone-select').val();
        const sortBy = $('#sort-select').val();
        
        // Make API request
        $.ajax({
            url: '/api/analyze',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                warzone: warzone,
                sort: sortBy
            }),
            success: function(response) {
                // Hide loading indicator
                $('#loading').hide();
                
                if (response.error) {
                    // Show error message
                    $('#error-container').text(response.error).show();
                } else {
                    // Show results
                    $('#results').html(response.html);
                    
                    // Show system search if not already shown
                    if (!hasAnalyzed) {
                        $('#system-search').slideDown();
                        hasAnalyzed = true;
                    }
                    
                    // Add event listeners to system links
                    addSystemLinkListeners();
                }
            },
            error: function(xhr, status, error) {
                // Hide loading indicator
                $('#loading').hide();
                
                // Show error message
                $('#error-container').text('Error: ' + error).show();
            }
        });
    });
    
    // Handle system search button click
    $('#search-btn').click(function() {
        const systemName = $('#system-input').val().trim();
        
        if (systemName) {
            // Show loading indicator
            $('#loading').show();
            $('#results').empty();
            $('#error-container').hide();
            
            // Make API request
            $.ajax({
                url: '/api/analyze',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    system: systemName
                }),
                success: function(response) {
                    // Hide loading indicator
                    $('#loading').hide();
                    
                    if (response.error) {
                        // Show error message
                        $('#error-container').text(response.error).show();
                    } else {
                        // Show results
                        $('#results').html(response.html);
                    }
                },
                error: function(xhr, status, error) {
                    // Hide loading indicator
                    $('#loading').hide();
                    
                    // Show error message
                    $('#error-container').text('Error: ' + error).show();
                }
            });
        }
    });
    
    // Handle Enter key in system input
    $('#system-input').keypress(function(e) {
        if (e.which === 13) {
            $('#search-btn').click();
        }
    });
    
    // Function to add event listeners to system links
    function addSystemLinkListeners() {
        $('.system-link').click(function(e) {
            e.preventDefault();
            
            const systemName = $(this).data('system');
            $('#system-input').val(systemName);
            $('#search-btn').click();
        });
    }
});

