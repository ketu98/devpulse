using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.DataContracts;
using Microsoft.ApplicationInsights.Extensibility;
using System;

class Program
{
    static void Main()
    {
        // Create a telemetry initializer to add custom properties
        var initializer = new TelemetryInitializer();
        initializer.Initialize(new TelemetryClient());

        // Create a new telemetry client
        var telemetryClient = new TelemetryClient(new TelemetryConfiguration());
        telemetryClient.TelemetryInitializers.Add(initializer);

        // Simulate a request with custom properties
        var requestTelemetry = new RequestTelemetry();
        requestTelemetry.Name = "HealthCheck";
        requestTelemetry.Properties["Endpoint"] = "https://api.example.com/health";
        requestTelemetry.Properties["Method"] = "GET";
        request-Telemetry.Properties["DurationMs"] = 120;

        // Record the request
        telemetryClient.TrackRequest(requestTelemetry);

        // Log a metric
        telemetryClient.TrackMetric("ResponseTimeMs", 120.0);

        // Log an event
        telemetryClient.TrackEvent("HealthCheckCompleted");

        Console.WriteLine("Application Insights data recorded successfully.");
        Console.ReadKey();
    }
}
