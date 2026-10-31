## What this demonstrates

This POC demonstrates how to monitor and analyze Azure Application Performance using Azure Application Insights with C#.

## How it works

The C# application logs performance data (e.g., request duration, errors) using Application Insights SDK. It captures telemetry such as page views, dependencies, and exceptions, sending them to Azure Application Insights. The data is then visualized in real-time dashboards, enabling performance tracking and troubleshooting.

## How to run

1. Install the Azure Application Insights SDK via NuGet: `Install-Package Microsoft.ApplicationInsights`.
2. Create a new console application in Visual Studio.
3. Add your instrumentation key from the Azure portal.
4. Replace the placeholder code with the sample telemetry logger.
5. Build and run the app. It will start logging performance data automatically.
6. Navigate to the Azure portal → Application Insights → Your app → Metrics to view real-time performance.

## Things to try

- Add custom events or exceptions.
- Integrate with a web API to monitor endpoint performance.
- Configure alerts for high error rates or slow response times.
