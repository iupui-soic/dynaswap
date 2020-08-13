<%@ include file="/WEB-INF/template/include.jsp"%>

<%@ include file="/WEB-INF/template/header.jsp"%>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Dynaswap Hierarchy Generation Interface</title>
    <!-- <link rel="stylesheet" href="../../static/css/style.css"> -->
    <style>
        #cy {
            width: 100%;
            height: 600px;
            display: block;
        }

        .fade-in {
            opacity: 1;
            animation-name: fadeInOpacity;
            animation-iteration-count: 1;
            animation-timing-function: ease-in;
            animation-duration: .25s;
        }

        @keyframes fadeInOpacity {
            0% {
                opacity: 0;
            }
            100% {
                opacity: 1;
            }
        }
    </style>
    <!-- should actually install at some point -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css">
</head>
<body>
    <section class="hero is-light">
        <div class="hero-body">
          <div class="container">
            <h1 class="title">
                Dynaswap Hierarchy Generation Interface
            </h1>
            <h2 class="subtitle">
                For creating directed acyclic graphs in hierarchical access control schemes
            </h2>
          </div>
        </div>
    </section>
    
    <section class="section">
        <section class="container is-fluid">
            <button id="create_dag" class="button is-success">Create the DAG</button>

            <!-- hidden by default, until dag is created -->
            <div id="cy" class="box is-hidden"></div>

            <hr class="hr">
        </section>
    </section>

    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/cytoscape@3.14.0/dist/cytoscape.min.js"></script> 
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js"></script> 
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.2.2/cytoscape-dagre.min.js"></script>
    <script type="text/javascript">
        //inline for now because I can't get openmrs to find the path
        console.log("hwllo world!!!");

        async function getData(url){
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            return response.json();
        }

        const createDAGBtn = document.querySelector("#create_dag");
        createDAGBtn.addEventListener("click", (e) => {
            e.preventDefault();
            getData('http://localhost:8080/openmrs/module/dynaswap/dag.json')
            .then((res) => {
                console.log(res);
                if(res.alert){
                    alert(res.alert);
                }
                // reveal box holding dag
                let cyEl = document.getElementById("cy");
                cyEl.classList.remove("is-hidden");
                cyEl.classList.add("fade-in");
                // box reveal changes dimensions so must resize
                cy.resize();
                // update the dag
                cy.json(res);
                cy.layout(dagreDefaults).run();

            });
        });
        
        // dagre settings
        // DANGEROUS global variables
        // needed by multiple event listener functions to properly render graph
        let cy;
        let dagreDefaults;

        document.addEventListener("DOMContentLoaded", ()=>{
            cy = cytoscape({
                container: document.getElementById("cy"),
            
                elements: [ // list of graph elements to start with
                    { // node a
                      data: { id: 'a' }
                    },
                    { // node b
                      data: { id: 'b' }
                    },
                    { // edge ab
                      data: { id: 'ab', source: 'a', target: 'b' }
                    }
                  ],
                
                    style: [ // the stylesheet for the graph
                        {
                        selector: 'node',
                        style: {
                            'background-color': '#666',
                            'label': 'data(id)'
                        }
                        },
                    
                        {
                        selector: 'edge',
                        style: {
                            'width': 3,
                            'line-color': '#ccc',
                            'target-arrow-color': '#ccc',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier'
                            }
                        }
                    ],
                
                    layout: {
                        name: 'dagre'
                    },

                    // interaction options
                    minZoom: 1e-1,
                    maxZoom: 1e1,
                    zoomingEnabled: true,
                    userPanningEnabled: true,
                    boxSelectionEnabled: true,
                    selectionType: 'single',
                    touchTapThreshold: 8,
                    desktopTapThreshold: 4,
                    autolock: false,
                    autoungrabify: false,
                    autounselectify: false,

                    // rendering options:
                    headless: false,
                    styleEnabled: true,
                    hideEdgesOnViewport: false,
                    textureOnViewport: false,
                    motionBlur: false,
                    motionBlurOpacity: 0.2,
                    wheelSensitivity: 1,
                    pixelRatio: 'auto'
            });

            dagreDefaults  = {
                name: "dagre",
                // dagre algo options, uses default value on undefined
                nodeSep: undefined, // the separation between adjacent nodes in the same rank
                edgeSep: undefined, // the separation between adjacent edges in the same rank
                rankSep: undefined, // the separation between each rank in the layout
                rankDir: undefined, // 'TB' for top to bottom flow, 'LR' for left to right,
                ranker: undefined, // Type of algorithm to assign a rank to each node in the input graph. Possible values: 'network-simplex', 'tight-tree' or 'longest-path'
                minLen: function( edge ){ return 1; }, // number of ranks to keep between the source and target of the edge
                edgeWeight: function( edge ){ return 1; }, // higher weight edges are generally made shorter and straighter than lower weight edges
              
                // general layout options
                fit: true, // whether to fit to viewport
                padding: 30, // fit padding
                spacingFactor: undefined, // Applies a multiplicative factor (>0) to expand or compress the overall area that the nodes take up
                nodeDimensionsIncludeLabels: false, // whether labels should be included in determining the space used by a node
                animate: false, // whether to transition the node positions
                animateFilter: function( node, i ){ return true; }, // whether to animate specific nodes when animation is on; non-animated nodes immediately go to their final positions
                animationDuration: 500, // duration of animation in ms if enabled
                animationEasing: undefined, // easing of animation if enabled
                boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
                transform: function( node, pos ){ return pos; }, // a function that applies a transform to the final node position
                ready: function(){}, // on layoutready
                stop: function(){} // on layoutstop
            };

            cy.layout(dagreDefaults).run();
        });
    </script>
</body>
</html>

<%@ include file="/WEB-INF/template/footer.jsp"%>
