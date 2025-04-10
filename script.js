document.addEventListener("DOMContentLoaded", function () {
  // Tab switching functionality
  const tabs = document.querySelectorAll(".tab");
  const tabContainers = document.querySelectorAll(".tab-container");
  const workflowEditor = document.querySelector(".workflow-editor");

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      // Remove active class from all tabs and hide all containers
      tabs.forEach((t) => t.classList.remove("active"));
      tabContainers.forEach((container) => {
        if (container) container.classList.remove("active");
      });

      // Add active class to clicked tab
      tab.classList.add("active");

      // Show appropriate content based on tab index
      if (index === 0) {
        // Show workflow editor
        workflowEditor.style.display = "block";
        // Hide other tab containers if they exist
        document
          .querySelectorAll(".chat-container, .agent-container")
          .forEach((el) => {
            if (el) el.style.display = "none";
          });
      } else if (index === 1) {
        // Show chat container, hide others
        workflowEditor.style.display = "none";
        const chatContainer = document.querySelector(".chat-container");
        if (chatContainer) {
          chatContainer.style.display = "flex";
        } else {
          // Redirect to qa-interface.html if not already loaded
          window.location.href = "qa-interface.html";
        }
        const agentContainer = document.querySelector(".agent-container");
        if (agentContainer) agentContainer.style.display = "none";
      } else if (index === 2) {
        // Show agent container, hide others
        workflowEditor.style.display = "none";
        const chatContainer = document.querySelector(".chat-container");
        if (chatContainer) chatContainer.style.display = "none";
        const agentContainer = document.querySelector(".agent-container");
        if (agentContainer) {
          agentContainer.style.display = "block";
        } else {
          // Redirect to custom-agent.html if not already loaded
          window.location.href = "custom-agent.html";
        }
      }
    });
  });

  // Drag and drop functionality for tools
  const toolItems = document.querySelectorAll(".tool-item");
  const canvas = document.querySelector(".canvas");

  if (canvas) {
    // Object to store connections
    const connections = [];
    // Keep track of ports for connections
    let startPort = null;
    let isDraggingConnection = false;

    toolItems.forEach((tool) => {
      tool.addEventListener("mousedown", (e) => {
        const toolType = tool.getAttribute("data-tool");
        createNode(toolType, e.clientX, e.clientY);
      });
    });

    // Function to create a node in the workflow editor
    function createNode(toolType, clientX, clientY) {
      const node = document.createElement("div");
      node.className = "node";
      node.dataset.tool = toolType;

      // Position node where user dropped it
      const canvasRect = canvas.getBoundingClientRect();
      const x = clientX - canvasRect.left - 110; // Center the node
      const y = clientY - canvasRect.top - 30; // Position near cursor

      node.style.left = `${x}px`;
      node.style.top = `${y}px`;

      // Add node contents based on tool type
      let nodeContent = "";
      let icon = "";
      let params = [];

      switch (toolType) {
        case "stdf-to-csv":
          icon = "fa-file-excel";
          params = [
            { name: "input_file", label: "输入STDF文件", type: "file" },
            {
              name: "output_format",
              label: "输出格式",
              type: "select",
              options: ["CSV", "XLSM"],
            },
            { name: "output_path", label: "输出路径", type: "text" },
          ];
          break;
        case "xlsm-to-html":
          icon = "fa-file-code";
          params = [
            { name: "input_file", label: "输入XLSM文件", type: "file" },
            {
              name: "template",
              label: "分析模板",
              type: "select",
              options: ["基础分析", "详细分析", "自定义"],
            },
            { name: "output_path", label: "输出HTML路径", type: "text" },
          ];
          break;
        case "xlsm-to-db":
          icon = "fa-database";
          params = [
            { name: "input_file", label: "输入XLSM文件", type: "file" },
            { name: "db_name", label: "数据库名称", type: "text" },
            { name: "output_path", label: "输出路径", type: "text" },
          ];
          break;
        case "defect-model-1":
        case "defect-model-2":
        case "defect-model-3":
          icon = "fa-bug";
          params = [
            { name: "input_data", label: "输入数据", type: "file" },
            { name: "threshold", label: "检测阈值", type: "text" },
            { name: "output_path", label: "输出报告路径", type: "text" },
          ];
          break;
        case "custom-model":
          icon = "fa-robot";
          params = [
            { name: "input_data", label: "输入数据", type: "file" },
            {
              name: "model_type",
              label: "模型类型",
              type: "select",
              options: ["通用分析", "缺陷分析", "性能预测"],
            },
            { name: "output_path", label: "输出报告路径", type: "text" },
          ];
          break;
      }

      // Create node header with tooltip
      nodeContent += `
        <div class="node-header">
          <i class="fas ${icon}"></i>
          <span>${getToolName(toolType)}</span>
        </div>
        <div class="node-content">
      `;

      // Create parameters
      params.forEach((param, index) => {
        nodeContent += `
          <div class="node-param">
            <label for="${toolType}-${param.name}">${param.label}</label>
        `;

        if (param.type === "select") {
          nodeContent += `<select id="${toolType}-${param.name}">`;
          param.options.forEach((option) => {
            nodeContent += `<option value="${option}">${option}</option>`;
          });
          nodeContent += `</select>`;
        } else {
          nodeContent += `<input type="${
            param.type === "file" ? "text" : param.type
          }" id="${toolType}-${param.name}" placeholder="${param.label}">`;
        }

        nodeContent += `</div>`;
      });

      // Add input/output ports
      nodeContent += `
        <div class="node-port input" data-position="input"></div>
        <div class="node-port output" data-position="output"></div>
      `;

      nodeContent += `</div>`;
      node.innerHTML = nodeContent;

      // Make node draggable
      makeDraggable(node);

      canvas.appendChild(node);

      // Set up the input and output ports
      const inputPort = node.querySelector(".node-port.input");
      const outputPort = node.querySelector(".node-port.output");

      // Position ports vertically centered
      inputPort.style.top = "50%";
      outputPort.style.top = "50%";

      // Add connection start event to output port
      setupPortConnections(outputPort, inputPort);

      return node;
    }

    // Setup port connection functionality
    function setupPortConnections(outputPort, inputPort) {
      // Start connection from output port
      outputPort.addEventListener("mousedown", function (e) {
        e.stopPropagation(); // Prevent node dragging
        startPort = outputPort;
        isDraggingConnection = true;

        // Create temporary connection line
        const tempConnection = document.createElement("div");
        tempConnection.className = "connection temp-connection";
        canvas.appendChild(tempConnection);

        // Get starting position
        const startNode = outputPort.closest(".node");
        const startRect = startNode.getBoundingClientRect();
        const canvasRect = canvas.getBoundingClientRect();

        // Set connection start at output port
        const startX = startRect.right - canvasRect.left;
        const startY = startRect.top - canvasRect.top + startRect.height / 2;

        // Update temporary connection on mouse move
        const mouseMoveHandler = function (e) {
          if (isDraggingConnection) {
            const endX = e.clientX - canvasRect.left;
            const endY = e.clientY - canvasRect.top;

            // Calculate distance and angle
            const dx = endX - startX;
            const dy = endY - startY;
            const length = Math.sqrt(dx * dx + dy * dy);
            const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

            // Position and rotate the connection line
            tempConnection.style.width = `${length}px`;
            tempConnection.style.left = `${startX}px`;
            tempConnection.style.top = `${startY}px`;
            tempConnection.style.transform = `rotate(${angle}deg)`;
            tempConnection.style.transformOrigin = "0 0";
          }
        };

        document.addEventListener("mousemove", mouseMoveHandler);

        // End connection on mouse up
        document.addEventListener("mouseup", function mouseUpHandler(e) {
          document.removeEventListener("mousemove", mouseMoveHandler);
          document.removeEventListener("mouseup", mouseUpHandler);

          // Check if we're over an input port
          const target = document.elementFromPoint(e.clientX, e.clientY);

          if (
            target &&
            target.classList.contains("node-port") &&
            target.dataset.position === "input" &&
            target !== inputPort
          ) {
            // Create permanent connection
            const endNode = target.closest(".node");
            createConnection(startNode, endNode);
          }

          // Remove temporary connection
          if (tempConnection && tempConnection.parentNode) {
            tempConnection.parentNode.removeChild(tempConnection);
          }

          isDraggingConnection = false;
          startPort = null;
        });
      });

      // Allow connections to end at input port
      inputPort.addEventListener("mouseup", function (e) {
        if (isDraggingConnection && startPort) {
          const startNode = startPort.closest(".node");
          const endNode = inputPort.closest(".node");

          if (startNode !== endNode) {
            createConnection(startNode, endNode);
          }
        }
      });
    }

    // Create a permanent connection between two nodes
    function createConnection(startNode, endNode) {
      // Already connected?
      const existingConnection = connections.find(
        (conn) => conn.start === startNode && conn.end === endNode
      );

      if (existingConnection) return;

      // Create connection DOM element
      const connection = document.createElement("div");
      connection.className = "connection";
      canvas.appendChild(connection);

      // Store connection info
      connections.push({
        start: startNode,
        end: endNode,
        element: connection,
      });

      // Update connection line
      updateConnection(startNode, endNode, connection);

      // Update connections when nodes move
      startNode.addEventListener("positionchange", function () {
        updateConnection(startNode, endNode, connection);
      });

      endNode.addEventListener("positionchange", function () {
        updateConnection(startNode, endNode, connection);
      });
    }

    // Update position and rotation of a connection line
    function updateConnection(startNode, endNode, connectionElem) {
      const startRect = startNode.getBoundingClientRect();
      const endRect = endNode.getBoundingClientRect();
      const canvasRect = canvas.getBoundingClientRect();

      // Find positions of output and input ports
      const startX = startRect.right - canvasRect.left;
      const startY = startRect.top - canvasRect.top + startRect.height / 2;
      const endX = endRect.left - canvasRect.left;
      const endY = endRect.top - canvasRect.top + endRect.height / 2;

      // Calculate distance and angle
      const dx = endX - startX;
      const dy = endY - startY;
      const length = Math.sqrt(dx * dx + dy * dy);
      const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

      // Position and rotate the connection line
      connectionElem.style.width = `${length}px`;
      connectionElem.style.left = `${startX}px`;
      connectionElem.style.top = `${startY}px`;
      connectionElem.style.transform = `rotate(${angle}deg)`;
      connectionElem.style.transformOrigin = "0 0";
    }

    // Helper function to get tool name
    function getToolName(toolType) {
      const toolMap = {
        "stdf-to-csv": "STDF转CSV",
        "xlsm-to-html": "XLSM转HTML分析",
        "xlsm-to-db": "XLSM转数据库",
        "defect-model-1": "缺陷模型检测1",
        "defect-model-2": "缺陷模型检测2",
        "defect-model-3": "缺陷模型检测3",
        "custom-model": "自定义大模型",
      };
      return toolMap[toolType] || toolType;
    }

    // Make elements draggable
    function makeDraggable(element) {
      let pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;

      const header = element.querySelector(".node-header");
      if (header) {
        // If there's a header, use it as drag handle
        header.addEventListener("mousedown", dragMouseDown);
      } else {
        // Otherwise use the whole element
        element.addEventListener("mousedown", dragMouseDown);
      }

      function dragMouseDown(e) {
        e.preventDefault();
        e.stopPropagation();

        // Check if we're clicking on a port (for connections)
        if (e.target.classList.contains("node-port")) {
          return;
        }

        // Get mouse position at startup
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.addEventListener("mouseup", closeDragElement);
        document.addEventListener("mousemove", elementDrag);
      }

      function elementDrag(e) {
        e.preventDefault();
        // Calculate new cursor position
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;

        // Set element's new position
        element.style.top = element.offsetTop - pos2 + "px";
        element.style.left = element.offsetLeft - pos1 + "px";

        // Trigger custom event for connection updates
        const event = new CustomEvent("positionchange");
        element.dispatchEvent(event);
      }

      function closeDragElement() {
        // Stop moving when mouse button is released
        document.removeEventListener("mouseup", closeDragElement);
        document.removeEventListener("mousemove", elementDrag);
      }
    }

    // Add sample nodes to demonstrate workflow
    setTimeout(() => {
      const node1 = createNode("stdf-to-csv", 300, 200);
      const node2 = createNode("xlsm-to-html", 600, 200);
      const node3 = createNode("defect-model-1", 900, 300);

      // Create connections between the sample nodes
      setTimeout(() => {
        createConnection(node1, node2);
        createConnection(node2, node3);
      }, 100);
    }, 500);
  }

  // Handle modal functionality
  const createAgentButton = document.querySelector(".create-agent");
  const modal = document.querySelector(".modal");

  if (createAgentButton && modal) {
    createAgentButton.addEventListener("click", function () {
      modal.style.display = "flex";
    });

    // Close modal when clicking the close button or outside
    const closeButton = modal.querySelector(".modal-header button");
    if (closeButton) {
      closeButton.addEventListener("click", function () {
        modal.style.display = "none";
      });
    }

    // Close modal when clicking outside
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });

    // Prevent closing when clicking inside modal content
    const modalContent = modal.querySelector(".modal-content");
    if (modalContent) {
      modalContent.addEventListener("click", function (e) {
        e.stopPropagation();
      });
    }
  }
});
