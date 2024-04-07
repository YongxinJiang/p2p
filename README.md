# p2p
This code implements a simple instant messaging system, including user, messaging system and server-side implementation.

The User class represents the users in the system, each user has a username, a connection to communicate with the client, and a list to store received messages.
The MessagingSystem class represents the messaging system and is responsible for registering users, initiating sessions, and storing offline messages.
The handle_client function is used to handle the client's connection, receive messages sent by the client and forward them to the corresponding user.
The start_server function starts the server, listens to the specified port, and creates a thread for each client connection.
By running the start_server function, we can start a server locally, allowing users to connect and send messages. Users can communicate with other users by sending messages to the server.

This code only implements basic instant messaging functions and can be expanded and optimized according to actual needs, such as adding user authentication, message encryption, persistent storage, etc.
