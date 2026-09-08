# Azure Service Bus Basics Overview

**Topic:** Azure Service Bus Basics  
**Category:** azure

# Azure Service Bus Basics Overview

Azure Service Bus is a messaging service that enables decoupled, scalable communication between services. At its core, it handles message routing, delivery, and persistence—key for building resilient, asynchronous systems.

In practice, Service Bus works with two main message types: queues and topics. A queue is a single-line, FIFO (first-in, first-out) structure where messages are processed one at a time. A topic, on the other hand, allows message routing to multiple subscriptions—useful when you want to fan out messages to different consumers.

I built a minimal proof-of-concept (POC) to test message flow between two microservices. One service published a message to a queue; the other subscribed to that queue and processed it. I used the Azure SDK for .NET to create a publisher and a receiver. The setup was straightforward: initialize a client, create a queue, send a message, and then listen for incoming messages. I observed message delivery was reliable—no loss, no duplicates—within a few seconds of publishing.

The POC revealed a few practical nuances. First, message size limits matter. Service Bus has a 256 KB limit per message, which is sufficient for most use cases but can be a constraint with large payloads. Second, message expiration and dead-letter queues help manage failures. I configured a 5-minute TTL and enabled dead-lettering, which let me see messages that couldn’t be processed. This helped simulate real-world error handling.

I also noticed that connection pooling and retry logic are essential. Without them, the client can quickly exhaust connections or fail on transient errors. I added exponential backoff with a max retry count, which improved stability during test spikes.

## What I learned

- Queues provide reliable, ordered delivery; topics enable dynamic routing.
- Message size limits are hard to exceed in most scenarios, but must be considered during design.
- Dead-letter queues are not optional—they help debug and recover from failed processing.
- Connection management and retry policies are critical for production-grade reliability.
- The SDKs are mature and well-documented, but error handling must be explicit.

## Key Takeaways

- Use queues for simple, reliable message delivery between services.
- Use topics with subscriptions when you need to route messages to multiple consumers.
- Always configure message TTL and dead-lettering to handle failures.
- Implement retry logic with backoff to handle transient network issues.
- Message size and payload structure should be validated early in design.

This isn’t a full messaging solution, but it’s a solid foundation for building decoupled, scalable components. For most backend services, Service Bus strikes a good balance between simplicity and capability—especially when used with proper error handling and monitoring.
