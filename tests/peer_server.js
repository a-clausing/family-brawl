// Local PeerJS matchmaking server for tests/net_peer.py: node tests/peer_server.js PORT
// (needs the `peer` package; net_peer.py installs it into tests/out/node_modules)
const { PeerServer } = require('peer');
const port = +(process.argv[2] || 9123);
PeerServer({ port, host: '127.0.0.1', path: '/' }, () => console.log('peer server on', port));
