const ws = require('ws');
const http = require('https');
const fs = require("fs")

const wss = new ws.Server({noServer: true});

//const clients = new Set();

let clients = {}

function getClientId(ws) {
    for (let id in clients) {
        if (clients[id] !== null && clients[id].ws === ws) { return id; }
    }
    return null;
}

function newUser(ws, id) {
    let token = Math.random().toString(36).slice(2);
    clients[id] = {
        "ws": ws,
        "token": token,
        "username": message.username,
    };
    ws.send(JSON.stringify({
        "protocol": "register",
        "id": id,
        "token": token
    }));
    console.log(`[client accepted] id: ${id} token: ${token}`);
}

function login(id, token, ws) {
    let client = clients[id];
    let isSuccess = client.token === token;
    if (isSuccess){
        clients[id] = {
            "ws": ws,
            "token": token,
            "username": client.username,
        };
    }
    ws.send(JSON.stringify({
        "protocol": "login",
        "id": id,
        "token": token,
        "isSuccess": isSuccess
    }));
    console.log(`[Client login] id: ${id} token: ${token} isSuccess: ${isSuccess}`);
}

function deleteUser(ws, id, token) {
    let client = clients[id];
    if (client.token === token) {
        client = null;
        console.log(`[Client delete] id: ${id} token: ${token}`);
    }
}

function onMessage(from, to, message) {
    let client = clients[from];
    let packet = JSON.stringify({
        "from" : from,
        "message" : message,
        "username" : client.username,
    })

    if (clients[to]) {
        clients[to].ws.send(packet);
    }
    console.log(`[message] from: ${from} to: ${to} msg: ${message}`);
}

function changeUsername(id, token, username) {
    let client = clients[id];
    if (client.token === token) {
        client.username = username;
    }
    client.ws.send(JSON.stringify({
        "protocol": "changeUsername",
        "id": id,
        "token": token,
        "username": username
    }));
}

function handleMessage(ws, message) {
    let id = getClientId(ws);

    switch(message.protocol) {
    case 'register':
        if (message.from === null) { break; }
        newUser(ws, message.from);
        break;
    case 'login':
        if (message.id === null || message.token === null) { break; }
        login(message.id, message.token, ws);
        break;
    case 'deleteUser':
        if (message.id === null || message.token === null) { break; }
        deleteUser(ws, message.from, message.token);
        break;
    case 'message':
        if (message.token === null || message.message === null) { break; }
        onMessage(id, message.to, message.message);
        break;
    case 'changeUsername':
        if (message.token === null || message.username === null) { break; }
        changeUsername(id, message.token, message.username);
        break;
    }
}

function onSocketConnect(ws) {
    console.log(`[client connect]`);

    ws.on('message', function(message) {
        message = JSON.parse(message);
        handleMessage(ws, message);
    });

    ws.on('close', function(event) {
        console.log(`[client disconnect] id: ${getClientId(ws)} `);
    });
}

let options = {
    key: fs.readFileSync("./pem/privkey.pem"),
    cert: fs.readFileSync("./pem/fullchain.pem"),
}

server = http.createServer(options, (req, res) => {
    wss.handleUpgrade(req, req.socket, Buffer.alloc(0), onSocketConnect);
}).listen(25500);
