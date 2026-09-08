## What this demonstrates

This POC demonstrates the basics of Azure Service Bus messaging using C#. It shows how to send and receive messages via a topic and subscription, illustrating core concepts like message routing, publishing, and consumption.

## How it works

The application creates a Service Bus topic and subscription. A sender publishes messages to the topic, and a receiver listens to the subscription to process incoming messages. Messages are sent asynchronously, and the receiver handles them in a loop, printing each message to the console.

## How to run

1. Install the Azure Service Bus SDK via NuGet: `Install-Package Microsoft.Azure.ServiceBus`
2. Replace the connection string in the code with a valid Service Bus connection string from your Azure account.
3. Build and run the project. The sender will publish messages, and the receiver will display them in real time.

## Things to try

- Add message properties like priority or custom headers.
- Test message persistence by enabling message storage.
- Modify the receiver to process messages in batches or with error handling.
- Add a timeout to the receive operation to simulate real-world delays.
