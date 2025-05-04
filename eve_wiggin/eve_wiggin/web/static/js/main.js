// Main JavaScript for EVE Wiggin web frontend

$(document).ready(function() {
    // Initialize theme based on user preference
    initializeTheme();
    
    // Handle theme toggle button click
    $('#theme-toggle').click(function() {
        toggleTheme();
    });
    
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
    
    // Handle generate graph button click
    $('#generate-graph-btn').click(function() {
        // Show loading indicator
        $('#loading').show();
        $('#error-container').hide();
        
        // Get selected warzone and filter options
        const warzone = $('#graph-warzone-select').val();
        const filter = $('#graph-filter-select').val();
        
        // Make API request
        $.ajax({
            url: '/api/graph',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                warzone: warzone,
                filter: filter
            }),
            success: function(response) {
                // Hide loading indicator
                $('#loading').hide();
                
                if (response.error) {
                    // Show error message
                    $('#error-container').text(response.error).show();
                } else {
                    // Render graph
                    renderGraph(response);
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
    
    // Function to render the graph using Cytoscape.js
    function renderGraph(graphData) {
        // Clear existing graph
        $('#graph-container').empty();
        
        // Initialize Cytoscape
        const cy = cytoscape({
            container: document.getElementById('graph-container'),
            elements: {
                nodes: graphData.nodes,
                edges: graphData.edges
            },
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#fff',
                        'text-outline-width': 2,
                        'text-outline-color': '#000',
                        'font-size': '12px',
                        'font-weight': 'bold'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 'data(width)',
                        'line-color': 'data(color)',
                        'curve-style': 'bezier'
                    }
                }
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 100,
                nodeOverlap: 20,
                refresh: 20,
                fit: true,
                padding: 30,
                randomize: false,
                componentSpacing: 100,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
            }
        });
        
        // Add node click event
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const systemName = node.data('label');
            
            // Set the system name in the search input and trigger search
            $('#system-input').val(systemName);
            $('#search-btn').click();
            
            // Switch to the data tab
            $('#data-tab').tab('show');
        });
        
        // Add hover effects
        cy.on('mouseover', 'node', function(evt) {
            const node = evt.target;
            node.style({
                'border-width': 4,
                'border-color': '#fff'
            });
        });
        
        cy.on('mouseout', 'node', function(evt) {
            const node = evt.target;
            // Reset to original style
            node.style({
                'border-width': node.data('contested') === 'CONTESTED' ? 4 : 2,
                'border-color': node.data('contested') === 'CONTESTED' ? '#FF0000' : '#000'
            });
        });
    }
    
    // Function to add event listeners to system links
    function addSystemLinkListeners() {
        $('.system-link').click(function(e) {
            e.preventDefault();
            
            const systemName = $(this).data('system');
            $('#system-input').val(systemName);
            $('#search-btn').click();
        });
    }
    
    // Function to initialize theme based on user preference
    function initializeTheme() {
        const savedTheme = localStorage.getItem('eve-wiggin-theme');
        
        if (savedTheme === 'dark') {
            setDarkMode();
        } else {
            setLightMode();
        }
    }
    
    // Function to toggle between light and dark themes
    function toggleTheme() {
        const currentTheme = $('html').attr('data-bs-theme');
        
        if (currentTheme === 'dark') {
            setLightMode();
            localStorage.setItem('eve-wiggin-theme', 'light');
        } else {
            setDarkMode();
            localStorage.setItem('eve-wiggin-theme', 'dark');
        }
    }
    
    // Function to set dark mode
    function setDarkMode() {
        $('html').attr('data-bs-theme', 'dark');
        $('#theme-toggle').html('<i class="fas fa-sun"></i> Light Mode');
        $('#theme-toggle').removeClass('btn-outline-light').addClass('btn-outline-warning');
    }
    
    // Function to set light mode
    function setLightMode() {
        $('html').attr('data-bs-theme', 'light');
        $('#theme-toggle').html('<i class="fas fa-moon"></i> Dark Mode');
        $('#theme-toggle').removeClass('btn-outline-warning').addClass('btn-outline-light');
    }
});
