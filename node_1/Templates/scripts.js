var main_ip = '{{data.ip}}';
var main_port = '{{data.port}}';
var url = `http://${main_ip}:${main_port}`;
var socket = io.connect(url);

socket.on('connect', function() {
    console.log('Connected to server');
    socket.emit('get_socket_list');  // Request list of active sockets
    getData(); // Request data initially
});

socket.on('socket_list', function(data) {
    console.log('Socket list received:', data);
    // Display the list of active sockets
    var socketList = document.getElementById('socket-list');
    socketList.innerHTML = '';
    data.sockets.forEach(function(port) {
        var item = document.createElement('li');
        item.textContent = `Socket ${port}`;
        socketList.appendChild(item);
    });
});

socket.on('data', function(data) {
    console.log('Data received:', data);
    // Update the data list
    updateDataList(data.data);
});

socket.on('highest_number', function(data) {
    console.log('Highest number received:', data);
    // Display the highest number
    var highestNumberDiv = document.getElementById('highest-number');
    highestNumberDiv.textContent = data.number;
});

function updateDataList(data) {
    var dataList = document.getElementById('data-list');
    dataList.innerHTML = '';  // Clear existing data list
    var names = data.map(person => person.name).join(', ');
    dataList.textContent = names;
}

async function fetchData(url, number) {
    let isValid = false;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                proposal_number: number,
                value: 1
            })
        });
        const data = await response.json();
        isValid = data.accepted === true;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
    return isValid;
}

function addPerson() {
    var nameInput = document.getElementById('name');
    var numberInput = document.getElementById('number');
    var name = nameInput.value.trim();
    var number = 1;

    var isValid = true;

    // Validate Name
    if (name === "") {
        document.getElementById('name-error').textContent = "Name is required.";
        isValid = false;
    } else {
        document.getElementById('name-error').textContent = "";
    }

    // Validate Number
    if (number === "") {
        document.getElementById('number-error').textContent = "Number is required.";
        isValid = false;
    } else if (isNaN(number)) {
        document.getElementById('number-error').textContent = "Number must be a valid number.";
        isValid = false;
    } else {
        document.getElementById('number-error'). textContent = "";
    }

    if (isValid) {
        socket.emit('update_data', {name: name, number: 1});
        nameInput.value = '';
        numberInput.value = '';
    }
}

function saveNumber() {
    var numberInput = document.getElementById('number');
    var number = numberInput.value.trim();

    var isValid = true;

    // Validate Number
    if (number === "") {
        document.getElementById('number-error').textContent = "Number is required.";
        isValid = false;
    } else if (isNaN(number)) {
        document.getElementById('number-error').textContent = "Number must be a valid number.";
        isValid = false;
    } else {
        document.getElementById('number-error').textContent = "";
    }
    isValid = fetchData(url + '/accept', number);
    if (isValid) {
        socket.emit('update_data', {name: '', number: number});
        numberInput.value = '';
    }
}

async function callApi() {
    try {
        const response = await fetch(url + '/data_transfer');
        const data = await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Call the function every 2 seconds
setInterval(callApi, 2000); // 2000 ms

// Request data from the server
function getData() {
    socket.emit('get_data');
    socket.emit('get_highest_number');
}

// Request data every second
setInterval(getData, 1000);
