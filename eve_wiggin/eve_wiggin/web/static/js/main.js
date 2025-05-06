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
    
    // Global variable to store the Cytoscape instance
    let cy = null;
    
    // Global variable to store node positions
    let savedPositions = {};
    
    // Global variable to track if positions have been modified
    let positionsModified = false;
    
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
        
        // First, load any saved positions
        $.ajax({
            url: '/api/node_positions',
            method: 'GET',
            data: {
                warzone: warzone
            },
            success: function(positionsResponse) {
                // Store the saved positions
                savedPositions = positionsResponse.positions || {};
                
                // Now get the graph data
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
                            // Render graph with saved positions
                            renderGraph(response);
                            
                            // Reset the modified flag
                            positionsModified = false;
                            
                            // Show save positions button
                            $('#save-positions-btn').show();
                            $('#save-default-positions-btn').show();
                        }
                    },
                    error: function(xhr, status, error) {
                        // Hide loading indicator
                        $('#loading').hide();
                        
                        // Show error message
                        $('#error-container').text('Error: ' + error).show();
                    }
                });
            },
            error: function(xhr, status, error) {
                // If we can't load positions, just continue with empty positions
                savedPositions = {};
                
                // Show error message (but don't block graph generation)
                console.error('Error loading saved positions: ' + error);
                
                // Continue with graph generation
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
                            // Render graph with default positions
                            renderGraph(response);
                            
                            // Reset the modified flag
                            positionsModified = false;
                            
                            // Show save positions button
                            $('#save-positions-btn').show();
                            $('#save-default-positions-btn').show();
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
    });
    
    // Handle save positions button click
    $('#save-positions-btn').click(function() {
        if (!cy || !positionsModified) {
            return; // No graph or no changes to save
        }
        
        // Show loading indicator
        $('#loading').show();
        
        // Get current positions of all nodes
        const positions = {};
        cy.nodes().forEach(function(node) {
            positions[node.id()] = {
                x: node.position('x'),
                y: node.position('y')
            };
        });
        
        // Save positions to server
        $.ajax({
            url: '/api/node_positions',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                positions: positions
            }),
            success: function(response) {
                // Hide loading indicator
                $('#loading').hide();
                
                if (response.error) {
                    // Show error message
                    $('#error-container').text(response.error).show();
                } else {
                    // Show success message
                    $('#success-message').text('Node positions saved successfully!').show();
                    setTimeout(function() {
                        $('#success-message').fadeOut();
                    }, 3000);
                    
                    // Update saved positions
                    savedPositions = positions;
                    
                    // Reset modified flag
                    positionsModified = false;
                }
            },
            error: function(xhr, status, error) {
                // Hide loading indicator
                $('#loading').hide();
                
                // Show error message
                $('#error-container').text('Error saving positions: ' + error).show();
            }
        });
    });
    
    // Handle save default positions button click
    $('#save-default-positions-btn').click(function() {
        if (!cy) {
            return; // No graph to save
        }
        
        // Show loading indicator
        $('#loading').show();
        
        // Get current positions of all nodes
        const positions = {};
        cy.nodes().forEach(function(node) {
            positions[node.id()] = {
                x: node.position('x'),
                y: node.position('y')
            };
        });
        
        // Get selected warzone
        const warzone = $('#graph-warzone-select').val();
        
        // Save positions as default to server
        $.ajax({
            url: '/api/default_node_positions',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                positions: positions
            }),
            success: function(response) {
                // Hide loading indicator
                $('#loading').hide();
                
                if (response.error) {
                    // Show error message
                    $('#error-container').text(response.error).show();
                } else {
                    // Show success message
                    $('#success-message').text('Default node positions saved for all users!').show();
                    setTimeout(function() {
                        $('#success-message').fadeOut();
                    }, 3000);
                }
            },
            error: function(xhr, status, error) {
                // Hide loading indicator
                $('#loading').hide();
                
                // Show error message
                $('#error-container').text('Error saving default positions: ' + error).show();
            }
        });
    });
    
    // Function to render the graph using Cytoscape.js
    function renderGraph(graphData) {
        // Clear existing graph
        $('#graph-container').empty();
        
        // Prepare layout options
        let layoutOptions;
        
        // Check if we have saved positions for any nodes
        const hasSavedPositions = Object.keys(savedPositions).length > 0;
        
        if (hasSavedPositions) {
            // Use preset layout with saved positions
            layoutOptions = {
                name: 'preset',
                positions: function(node) {
                    // If we have a saved position for this node, use it
                    if (savedPositions[node.id()]) {
                        return savedPositions[node.id()];
                    }
                    // Otherwise, use a default position (center of the viewport)
                    return { x: 300, y: 300 };
                },
                fit: true,
                padding: 30
            };
        } else {
            // Use cose layout for automatic positioning
            layoutOptions = {
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
            };
        }
        
        // Initialize Cytoscape
        cy = cytoscape({
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
            layout: layoutOptions
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
            const nodeData = node.data();
            const position = node.renderedPosition();
            const containerRect = document.getElementById('graph-container').getBoundingClientRect();
            
            // Update node style
            node.style({
                'border-width': 4,
                'border-color': '#fff'
            });
            
            // Populate info card
            $('#node-info-header').text(nodeData.label);
            
            // Create content for the info card
            let content = '';
            
            // Region
            content += `<div class="info-label">Region:</div>`;
            content += `<div class="info-value">${nodeData.region_name}</div>`;
            
            // Owner and Occupier
            content += `<div class="info-label">Owner:</div>`;
            content += `<div class="info-value">
                <span class="info-badge" style="background-color: ${getFactionColor(nodeData.owner_faction_id)}">
                    ${nodeData.owner_faction_name}
                </span>
            </div>`;
            
            content += `<div class="info-label">Occupier:</div>`;
            content += `<div class="info-value">
                <span class="info-badge" style="background-color: ${getFactionColor(nodeData.occupier_faction_id)}">
                    ${nodeData.occupier_faction_name}
                </span>
            </div>`;
            
            // Adjacency type
            content += `<div class="info-label">Adjacency Type:</div>`;
            content += `<div class="info-value">
                <span class="info-badge" style="background-color: ${getAdjacencyColor(nodeData.adjacency)}">
                    ${nodeData.adjacency}
                </span>
            </div>`;
            
            // Contest status
            content += `<div class="info-label">Status:</div>`;
            content += `<div class="info-value">
                <span class="info-badge" style="background-color: ${nodeData.contested === 'CONTESTED' ? '#FF0000' : '#28a745'}">
                    ${nodeData.contested === 'CONTESTED' ? 'CONTESTED' : 'STABLE'}
                </span>
                ${nodeData.contest_percent ? `(${nodeData.contest_percent.toFixed(1)}%)` : ''}
            </div>`;
            
            // Advantage
            if (nodeData.hasOwnProperty('amarr_advantage') && nodeData.hasOwnProperty('minmatar_advantage')) {
                content += `<div class="info-label">Advantage:</div>`;
                content += `<div class="info-value">`;
                content += `Amarr: <span style="color: #FFD700">${nodeData.amarr_advantage.toFixed(2)}</span><br>`;
                content += `Minmatar: <span style="color: #FF4500">${nodeData.minmatar_advantage.toFixed(2)}</span><br>`;
                content += `Net: <span style="color: ${getNetAdvantageColor(nodeData.net_advantage)}">${nodeData.net_advantage.toFixed(2)}</span>`;
                content += `</div>`;
            }
            
            // Set content
            $('#node-info-content').html(content);
            
            // Position the info card
            const infoCard = $('#node-info-card');
            
            // Calculate position relative to the graph container
            // This is the key change - use position relative to the container, not the page
            let leftPos = position.x + 20;
            let topPos = position.y - 20;
            
            // Adjust position to keep the card within the viewport
            const cardWidth = 300;
            const cardHeight = infoCard.outerHeight() || 300;
            
            // Check if the card would go off the right edge of the container
            if (leftPos + cardWidth > containerRect.width) {
                leftPos = position.x - cardWidth - 20;
            }
            
            // Check if the card would go off the bottom of the container
            if (topPos + cardHeight > containerRect.height) {
                topPos = containerRect.height - cardHeight - 10;
            }
            
            // Check if the card would go off the top of the container
            if (topPos < 0) {
                topPos = 10;
            }
            
            // Set position and show the card
            infoCard.css({
                left: leftPos + 'px',
                top: topPos + 'px',
                display: 'block',
                opacity: 1
            });
        });
        
        cy.on('mouseout', 'node', function(evt) {
            const node = evt.target;
            // Reset to original style
            node.style({
                'border-width': node.data('contested') === 'CONTESTED' ? 4 : 2,
                'border-color': node.data('contested') === 'CONTESTED' ? '#FF0000' : '#000'
            });
            
            // Hide info card
            $('#node-info-card').css({
                opacity: 0,
                display: 'none'
            });
        });
        
        // Track position changes
        cy.on('dragfree', 'node', function() {
            positionsModified = true;
            
            // Show save reminder if positions have been modified
            $('#position-reminder').show();
            setTimeout(function() {
                $('#position-reminder').fadeOut();
            }, 3000);
        });
    }
    
    // Helper function to get faction color
    function getFactionColor(factionId) {
        const factionColors = {
            500001: "#FFD700",  // Amarr Empire
            500002: "#FF4500",  // Minmatar Republic
            500003: "#1E90FF",  // Caldari State
            500004: "#32CD32"   // Gallente Federation
        };
        
        return factionColors[factionId] || "#FFFFFF";
    }
    
    // Helper function to get adjacency color
    function getAdjacencyColor(adjacency) {
        const adjacencyColors = {
            "FRONTLINE": "#FF6347",         // Tomato
            "COMMAND_OPERATIONS": "#FFD700", // Gold
            "REARGUARD": "#32CD32"          // Lime Green
        };
        
        return adjacencyColors[adjacency] || "#FFFFFF";
    }
    
    // Helper function to get net advantage color
    function getNetAdvantageColor(netAdvantage) {
        if (netAdvantage > 0.1) {
            return "#FF4500";  // Red-Orange for Minmatar advantage
        } else if (netAdvantage < -0.1) {
            return "#FFD700";  // Gold for Amarr advantage
        } else {
            return "#FFFFFF";  // White for neutral
        }
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
