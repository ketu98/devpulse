using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.OutputCaching;

[ApiController]
[Route("[controller]")]
public class OutputCacheController : ControllerBase
{
    [HttpGet("example")]
    [ResponseCache(Duration = 60, Location = ResponseCacheLocation.Any)]
    public IActionResult GetExample()
    {
        // Simulate a slow operation
        System.Threading.Thread.Sleep(100);
        
        return Ok(new { Message = "This response is cached for 60 seconds.", Timestamp = DateTime.UtcNow });
    }

    [HttpGet("no-cache")]
    public IActionResult GetNoCache()
    {
        return Ok(new { Message = "This is not cached.", Timestamp = DateTime.UtcNow });
    }
}
