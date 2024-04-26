# p2p
This code implements a simple instant messaging system, including user, messaging system and server-side implementation.

The User class represents the users in the system, each user has a username, a connection to communicate with the client, and a list to store received messages.
The MessagingSystem class represents the messaging system and is responsible for registering users, initiating sessions, and storing offline messages.
The handle_client function is used to handle the client's connection, receive messages sent by the client and forward them to the corresponding user.
The start_server function starts the server, listens to the specified port, and creates a thread for each client connection.
By running the start_server function, we can start a server locally, allowing users to connect and send messages. Users can communicate with other users by sending messages to the server.

This code only implements basic instant messaging functions and can be expanded and optimized according to actual needs, such as adding user authentication, message encryption, persistent storage, etc.
the code utilizes parameterized queries to prevent SQL injection attacks. Specifically, when the server receives a register command and the message length is 4, the code extracts the username, password, and port from the message and executes two SQL queries using parameterized queries: one to check if the username already exists and another to insert a new user.
When checking if the username exists, the code uses a parameterized query with a ? placeholder, ensuring that the user-provided username does not affect the query itself, thus avoiding the risk of SQL injection.
Similarly, when inserting a new user, parameterized queries are used to ensure that user-provided data such as username, password, IP address, and port are not treated as part of the SQL query, thus mitigating the risk of SQL injection.
