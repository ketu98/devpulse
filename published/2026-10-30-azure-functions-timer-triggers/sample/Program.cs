using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Azure.Functions.Worker.Http.Tasks;
using System;
using System.Threading.Tasks;

record struct WorkloadData(string Message, DateTime Timestamp);

public class TimerTriggerFunction
{
    [Function("TimerTrigger")]
    public async Task<IActionResult> Run(
        [TimerTrigger("0 0 12 * * *")] TimerInfo timerInfo,
        HttpRequestData req,
        FunctionContext context)
    {
        var data = new WorkloadData(
            $"Workload executed at {DateTime.Now:yyyy-MM-dd HH:mm:ss}",
            DateTime.Now);

        // Log the execution with precision
        context.Log($"Timer triggered: {timerInfo.Schedule}");
        
        // Simulate a workload (e.g., processing, data aggregation)
        await Task.Delay(100); // Simulate work
        
        return new OkObjectResult(data);
    }
}
